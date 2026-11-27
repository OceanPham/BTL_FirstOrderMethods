/* Pure functions shared by the teaching simulations and numerical tests. */
(function (root) {
  "use strict";
  const data = Object.freeze([{x:1,y:1},{x:2,y:3},{x:3,y:2}]);
  const schedules = {gd:[[0,1,2],[0,1,2],[0,1,2]],sgd:[[0],[1],[2]],mb:[[0,1],[2,0],[1,2]]};
  function loss(w) { return data.reduce((sum,p)=>sum+(w*p.x-p.y)**2,0)/(2*data.length); }
  function step(w, method, k, rate) {
    if (!schedules[method] || !Number.isInteger(k) || k<0 || k>2) throw new Error("Bước phải nằm trong 0..2.");
    if (!Number.isFinite(w) || !Number.isFinite(rate) || rate<=0) throw new Error("Tham số hoặc tốc độ học không hợp lệ.");
    const batch=schedules[method][k].slice();
    const terms=data.map((p,i)=>({i, ...p, prediction:w*p.x,residual:w*p.x-p.y,gradient:(w*p.x-p.y)*p.x,used:batch.includes(i)}));
    const g=terms.filter(p=>p.used).reduce((s,p)=>s+p.gradient,0)/batch.length;
    const next=w-rate*g;
    return {before:w,g,next,loss:loss(next),batch,terms,k:k+1,rate};
  }
  function quadratic(z, rate) {
    if(!Number.isFinite(z)||!Number.isFinite(rate)||rate<=0)throw new Error("Số không hợp lệ");
    return z-rate*2*z;
  }
  const api={data,schedules,loss,step,quadratic,wStar:13/14,jStar:9/28};
  root.GuideMath=api;
  if(typeof module!=="undefined"&&module.exports)module.exports=api;
})(typeof window!=="undefined"?window:globalThis);
