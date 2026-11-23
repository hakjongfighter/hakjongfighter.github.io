// 학종파이터 자체 방문 집계 (GA4와 별개로 우리 서버에 직접 기록)
//  - 쿠키를 쓰지 않고, IP 주소도 저장하지 않아요. 브라우저에 무작위 번호만 하나 둬요.
//  - 관리자 기기(방문 현황 페이지를 연 브라우저)는 hf_internal=1 이라 집계에서 빠져요.
//  - 기록: 페이지 열람(pv), 버튼 등 행동(ev), 머문 시간·스크롤(eng)
(function () {
  'use strict';
  var me = document.currentScript;
  var API = ((me && me.getAttribute('data-api')) || 'https://hakjongfighter-blog-api.avecvalse.workers.dev').replace(/\/$/, '');
  var path = location.pathname.replace(/index\.html$/, '');
  if (/^\/(stats|blog\/admin)(\/|$)/.test(path)) return;      // 관리 화면은 세지 않음
  if (navigator.webdriver) return;                             // 자동화 브라우저
  if (/bot|crawl|spider|headless|lighthouse|pagespeed|preview/i.test(navigator.userAgent || '')) return;

  var LS = null;
  try { LS = window.localStorage; LS.getItem('hf_vid'); } catch (e) { LS = null; }
  if (LS && LS.getItem('hf_internal') === '1') return;         // 운영자 본인 방문 제외

  function rid() {
    var a = new Uint8Array(12), s = '';
    (window.crypto || window.msCrypto).getRandomValues(a);
    for (var i = 0; i < a.length; i++) s += ('0' + a[i].toString(16)).slice(-2);
    return s;
  }
  function get(k) { try { return LS ? LS.getItem(k) : null; } catch (e) { return null; } }
  function set(k, v) { try { if (LS) LS.setItem(k, v); } catch (e) {} }

  var vid = get('hf_vid');
  if (!vid) { vid = rid(); set('hf_vid', vid); }

  // 방문(세션): 30분 넘게 조용하면 새 방문으로 봐요. 처음 들어온 경로를 방문 내내 기억해요.
  var now = Date.now(), ses = null;
  try { ses = JSON.parse(get('hf_ses') || 'null'); } catch (e) { ses = null; }
  var q = new URLSearchParams(location.search);
  var ref = document.referrer || '', sameSite = false, prev = '';
  try { var ru = new URL(ref); sameSite = ru.hostname === location.hostname; if (sameSite) prev = ru.pathname.replace(/index\.html$/, ''); } catch (e) {}
  var hasUtm = !!q.get('utm_source');
  if (!ses || !ses.id || now - (ses.last || 0) > 30 * 60 * 1000 || hasUtm || (ref && !sameSite && ref !== ses.ref)) {
    ses = { id: rid(), ref: sameSite ? '' : ref.slice(0, 300), us: (q.get('utm_source') || '').slice(0, 60), um: (q.get('utm_medium') || '').slice(0, 60), uc: (q.get('utm_campaign') || '').slice(0, 80), land: path };
  }
  ses.last = now; set('hf_ses', JSON.stringify(ses));

  function send(o) {
    o.v = vid; o.s = ses.id; o.p = path; o.pp = prev;
    o.r = ses.ref; o.us = ses.us; o.um = ses.um; o.uc = ses.uc; o.l = ses.land;
    o.w = window.innerWidth || 0;
    var b = JSON.stringify(o);
    try { if (navigator.sendBeacon && navigator.sendBeacon(API + '/api/t', new Blob([b], { type: 'text/plain' }))) return; } catch (e) {}
    try { fetch(API + '/api/t', { method: 'POST', body: b, keepalive: true, headers: { 'Content-Type': 'text/plain' } }).catch(function () {}); } catch (e) {}
  }

  send({ t: 'pv', ti: (document.title || '').slice(0, 120) });

  // 버튼 등 행동: 기존 hfTrack(GA4용)을 감싸서 우리 서버에도 같이 보내요.
  var old = window.hfTrack;
  window.hfTrack = function (name, params) {
    try { if (typeof old === 'function') old(name, params); } catch (e) {}
    try {
      var keep = {}, n = 0;
      for (var k in (params || {})) { if (n++ < 6) keep[k] = String(params[k]).slice(0, 80); }
      send({ t: 'ev', n: String(name).slice(0, 40), pr: keep });
    } catch (e) {}
  };

  // 신청서 작성 시작 (첫 입력)
  var started = false;
  document.addEventListener('focusin', function (e) {
    if (started || !e.target || !e.target.closest) return;
    if (e.target.closest('#csForm')) { started = true; window.hfTrack('form_start', {}); }
  });

  // 머문 시간(화면이 보이는 동안만)과 가장 깊이 내려간 스크롤 위치
  var visibleSince = document.visibilityState === 'visible' ? Date.now() : 0, maxScroll = 0, sentScroll = -1;
  function depth() {
    var h = document.documentElement, full = Math.max(h.scrollHeight, document.body ? document.body.scrollHeight : 0) - window.innerHeight;
    var d = full <= 0 ? 100 : Math.round((window.pageYOffset || h.scrollTop || 0) / full * 100);
    if (d > maxScroll) maxScroll = Math.min(100, d);
  }
  window.addEventListener('scroll', depth, { passive: true });
  window.addEventListener('load', depth);
  function flush() {
    depth();
    var ms = visibleSince ? Date.now() - visibleSince : 0;
    visibleSince = 0;
    if (ms < 500 && maxScroll === sentScroll) return;
    sentScroll = maxScroll;
    send({ t: 'eng', ms: Math.min(ms, 30 * 60 * 1000), sc: maxScroll });
    ses.last = Date.now(); set('hf_ses', JSON.stringify(ses));
  }
  document.addEventListener('visibilitychange', function () {
    if (document.visibilityState === 'hidden') flush(); else visibleSince = Date.now();
  });
  window.addEventListener('pagehide', flush);
})();
