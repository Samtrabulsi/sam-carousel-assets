// Reading-time warp: real time T (0–90s) -> scene time t (0–60s).
// Entrances/exits play at normal speed; the "hold" between them is stretched for reading.
window.WARP=(()=>{
  const S=[0,2.6,4.4,6.2,8.0,9.3,12.0,13.85,15.45,17.0,21.5,26.0,31.0,39.0,44.0,46.9,49.5,53.5,60.0];
  const L=[4,2.5,3,3,1.5,4,3.5,3.5,3,7,6.5,6.5,11,6.5,5,5,6,8.5];
  const X=.45, segs=[]; let R=0;
  for(let i=0;i<L.length;i++){const D=S[i+1]-S[i], E=Math.min(1.3,D-0.5), A=E+X, H=D-A; segs.push({S0:S[i],D,E,A,H,R0:R,L:L[i]}); R+=L[i];}
  const total=R;
  function warp(T){ for(const g of segs){ if(T<g.R0+g.L||g===segs[segs.length-1]){ const u=T-g.R0;
      if(u<g.E) return g.S0+u; if(u<g.L-X) return g.S0+g.E+(u-g.E)*g.H/(g.L-g.A); return Math.min(g.S0+g.D, g.S0+g.D-(g.L-u)); } } return 60; }
  return {warp,total};
})();
