// Supply a connected Playwright page plus the explicit public preview base URL.
// This checks frontend serialization and restores the previous graph; no /prompt.
async (page, options = {}) => {
  const base = options.baseURL;
  if (!base || !['127.0.0.1','localhost','[::1]'].includes(new URL(base).hostname)) throw new Error('Supply a loopback LightStory preview baseURL');
  const catalog = await (await page.request.get(new URL('workflows/catalog.json', base).href)).json();
  const selected = options.selected || [];
  const rows = selected.length ? catalog.filter(row => selected.includes(row.model + '/' + row.function)) : catalog;
  if (selected.length && rows.length !== selected.length) throw new Error('Unknown workflow selection');
  const previous = await page.evaluate(async () => { const { app } = await import('/scripts/app.js'); return app.graph.serialize(); });
  const records = [];
  try {
    for (const row of rows) {
      const workflow = await (await page.request.get(new URL(row.workflow, base).href)).json();
      const expected = await (await page.request.get(new URL(row.api, base).href)).json();
      const record = await page.evaluate(async ({workflow, expected, label, strictTimeline}) => {
        const { app } = await import('/scripts/app.js');
        workflow.id = crypto.randomUUID();
        await app.loadGraphData(workflow, true, true, 'LightStory serialization check');
        await new Promise(resolve => setTimeout(resolve, 450));
        const result = await app.graphToPrompt();
        const errors = [];
        const subset = (want,have,path) => {
          if (want !== null && typeof want === 'object') {
            for (const [k,v] of Object.entries(want)) subset(v,have?.[k],path+'.'+k);
          } else if (JSON.stringify(want) !== JSON.stringify(have)) errors.push(path+': expected '+JSON.stringify(want)+'; got '+JSON.stringify(have));
        };
        for (const [id,node] of Object.entries(expected)) {
          const actual = result.output[id];
          if (!actual || actual.class_type !== node.class_type) {errors.push(id+': missing/wrong node type');continue;}
          for (const [key,value] of Object.entries(node.inputs)) {
            if (key === 'timeline_data') {
              if (strictTimeline) {
                const wanted=JSON.parse(value),got=JSON.parse(actual.inputs[key]);
                const essential=t=>({totalFrames:t.totalFrames,frameRate:t.frameRate,width:t.width,height:t.height,output:t.output,global:t.global,segments:t.segments});
                subset(essential(wanted),essential(got),id+'/timeline_data');
              }
              continue;
            }
            if (key === 'viewport_state' || key.startsWith('bd_grp_')) continue;
            if (JSON.stringify(actual.inputs[key]) !== JSON.stringify(value)) errors.push(id+'/'+key+': '+JSON.stringify(value)+' -> '+JSON.stringify(actual.inputs[key]));
          }
        }
        return {function:label,errors,missingNodeTypes:app.graph._nodes.filter(n=>!window.LiteGraph.registered_node_types[n.type]).map(n=>n.type),flaggedNodes:app.graph._nodes.filter(n=>n.has_errors).map(n=>({id:n.id,type:n.type})),api:result.output};
      },{workflow,expected,label:row.model+'/'+row.function,strictTimeline:options.strictTimeline === true});
      records.push(record);
    }
  } finally {
    await page.evaluate(async original => { const { app } = await import('/scripts/app.js'); await app.loadGraphData(original,true,true,'Restore previous graph'); },previous);
  }
  return records;
}
