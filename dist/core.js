/* Pure reader state, disclosure and search helpers. No network or storage access. */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.AtlasCore = factory();
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  const VERSION = '0.4.0';
  const chapter = v => Math.max(1, Math.min(34, Math.floor(Number(v) || 1)));
  const defaults = () => ({chapter:1, phase:'beginning', mode:'reading', group:'Carl', event:'latest', node:null, route:null, query:'', filter:'all', inferred:false, panel:null});
  const cutoff = s => s.mode === 'reference' ? 34 : s.phase === 'beginning' ? s.chapter - 1 : s.chapter;
  const primary = r => r.tier === 'primary' || (r.sources || []).includes('official');
  const known = (r,s) => !!r && (s.mode === 'reference' || (Number.isInteger(r.chapter) && (r.chapter <= cutoff(s) || (primary(r) && r.chapter === 1))));
  const memberships = (n,s) => (n.routes || []).filter(id => s.mode === 'reference' || (n.routeChapters[id] || n.chapter) <= cutoff(s) || (primary(n) && id === 'red'));
  const number = (n,s,route=s.route) => ((s.mode === 'reference' || cutoff(s) >= 14) && (route ? n.aliases[route] : n.aliases.nightmare)) || String(n.number);
  function model(D,s) {
    const N = new Map(D.nodes.map(n=>[n.id,n]));
    const R = new Map(D.routes.map(r=>[r.id,r]));
    const nodes = D.nodes.filter(n=>known(n,s));
    const routeVisible = r => s.mode === 'reference' || known(r,s) || nodes.some(n=>memberships(n,s).includes(r.id));
    const routes = D.routes.filter(routeVisible);
    const events = D.events.filter(e=>known(e,s));
    const groups = [...new Set(events.map(e=>e.group))];
    const edges = D.edges.filter(e=>known(e,s) && known(N.get(e.from),s) && known(N.get(e.to),s) && (e.kind !== 'sequence' || s.inferred));
    const routeName = id => R.get(id)?.name || 'Service unresolved';
    const context = n => memberships(n,s).map(routeName).join(' / ') || 'Line unresolved';
    const label = (n,route) => n.kind.includes('yard') ? n.name : `${number(n,s,route)}${n.name ? ' - '+n.name : ''}`;
    const title = n => n.kind.includes('yard') ? n.name : `${context(n)} ${label(n)}`;
    const groupEvents = (g=s.group) => events.filter(e=>e.group===g).sort((a,b)=>a.chapter-b.chapter || a.order-b.order);
    const reports = groupEvents();
    const report = reports.find(e=>e.id===s.event) || reports.at(-1) || null;
    const reportNodes = e => (e?.location ? [e.location] : e?.travel ? [e.travel.from,e.travel.to].filter(Boolean) : []).map(id=>N.get(id)).filter(n=>known(n,s));
    const locationText = id => known(N.get(id),s) ? title(N.get(id)) : 'Location unavailable at this reading point';
    const reportText = e => !e ? 'No recorded position at this reading point' : e.travel ? (e.travel.from ? locationText(e.travel.from)+' to '+locationText(e.travel.to) : 'Approaching '+locationText(e.travel.to)) : e.location ? locationText(e.location) : 'Rail position unresolved';
    return {N,R,nodes,routes,edges,events,groups,context,label,title,routeName,groupEvents,report,reportNodes,reportText};
  }
  function clean(D, input={}) {
    const s=Object.assign(defaults(),input);
    s.chapter=chapter(s.chapter); s.phase=s.phase==='finished'?'finished':'beginning';
    s.mode=s.mode==='reference'?'reference':'reading'; s.inferred=s.inferred===true;
    s.query=String(s.query || '').slice(0,120);
    if (!['all','stations','lines','yards','reports'].includes(s.filter)) s.filter='all';
    if (!['search','detail'].includes(s.panel)) s.panel=null;
    const m=model(D,s);
    if (!m.groups.includes(s.group)) s.group=m.groups[0] || 'Carl';
    if (!m.events.some(e=>e.id===s.event && e.group===s.group)) s.event='latest';
    if (!m.nodes.some(n=>n.id===s.node)) s.node=null;
    if (!m.routes.some(r=>r.id===s.route)) s.route=null;
    return s;
  }
  const reset = s => ({...s, node:null, route:null, query:'', filter:'all', inferred:false, panel:null});
  const norm = s => String(s).normalize('NFKD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/[^a-z0-9]+/g,' ').trim();
  const spellings = {mendaro:'mindaro',fulvis:'fulvous',vermilion:'vermillion',katya:'katia'};
  function distance(a,b) {
    const row=Array.from({length:b.length+1},(_,i)=>i);
    for(let i=1;i<=a.length;i++){let diagonal=row[0];row[0]=i;for(let j=1;j<=b.length;j++){const old=row[j];row[j]=Math.min(row[j]+1,row[j-1]+1,diagonal+(a[i-1]===b[j-1]?0:1));diagonal=old;}}
    return row[b.length];
  }
  function search(D,s) {
    const m=model(D,s), raw=norm(s.query), q=raw.split(' ').map(t=>spellings[t]||t).join(' ');
    const numeric=q.replace(/\s/g,'').match(/^(\d+)([ab])?$/);
    const tokens=q.split(' ').filter(Boolean), match = text => {
      const words=norm(text).split(' ');
      return tokens.every(t=>words.some(w=> /^\d+$/.test(t)?w===t : w.startsWith(t) || (t.length>=5 && distance(t,w)<=1)));
    };
    const results=[];
    for(const n of m.nodes){
      const kind=n.kind.includes('yard')?'yards':'stations';
      const text=`${m.title(n)} ${kind==='yards'?'yard '+n.name.split(' ').at(-1):'station'}`;
      const isMatch=numeric ? n.number===Number(numeric[1]) && (!numeric[2] || number(n,s,'nightmare').replace(/[^a-z0-9]/gi,'')===numeric[1]+numeric[2]) : match(text);
      if(isMatch) results.push({kind,id:n.id,heading:m.label(n),sub:m.context(n),badge:n.kind.includes('yard')?n.name.split(' ').at(-1):number(n,s)});
    }
    if(!numeric){
      for(const r of m.routes) if(match(r.name)) results.push({kind:'lines',id:r.id,heading:r.name,sub:`${m.nodes.filter(n=>memberships(n,s).includes(r.id)).length} indexed points; not a timetable`,color:r.color});
      for(const e of m.events) if(match(e.group+' '+m.reportText(e))) results.push({kind:'reports',id:e.id,heading:e.group,sub:`Chapter ${e.chapter} / ${m.reportText(e)}`,badge:'Ch '+e.chapter});
    }
    return {results:results.filter(r=>s.filter==='all'||r.kind===s.filter),normalized:q,corrected:q!==raw};
  }
  function hash(s) {
    const p=new URLSearchParams({v:VERSION,ch:String(s.chapter),phase:s.phase,mode:s.mode,follow:s.group});
    if(s.node)p.set('station',s.node);if(s.route)p.set('line',s.route);if(s.event!=='latest')p.set('checkpoint',s.event);
    if(s.query)p.set('q',s.query);if(s.inferred)p.set('inferred','1');if(s.filter!=='all')p.set('filter',s.filter);
    return '#'+p.toString();
  }
  function parse(D,fragment) {
    const p=new URLSearchParams(fragment.replace(/^#/,''));
    if(!['ch','station','line','checkpoint'].some(k=>p.has(k)))return null;
    // Old links used 'through chapter', so preserve that semantic.
    return clean(D,{chapter:chapter(p.get('ch')),phase:p.get('phase')||'finished',mode:p.get('mode'),group:p.get('follow'),event:p.get('checkpoint'),node:p.get('station'),route:p.get('line'),query:p.get('q'),inferred:p.get('inferred')==='1',filter:p.get('filter'),panel:(p.has('station')||p.has('line'))?'detail':null});
  }
  function connectionText(kind){return kind==='sequence'?'Number-order guide only; connection and direction unverified':kind==='ordered'?'Source-listed circuit order; not a live train direction':'Reported journey segment; intermediate stops may be omitted'}
  return {VERSION,defaults,chapter,cutoff,primary,known,memberships,number,model,clean,reset,norm,search,hash,parse,connectionText};
});
