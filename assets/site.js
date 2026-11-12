/* Карусель фото в посте и просмотр на весь экран */
(function () {
  var car = document.querySelector('[data-carousel]');
  if (!car) return;
  var track = car.querySelector('.car-track');
  var slides = Array.prototype.slice.call(car.querySelectorAll('.car-slide'));
  var n = slides.length;
  var count = car.querySelector('.car-count');
  var cur = 0;

  function go(i) {
    cur = (i + n) % n;
    track.scrollTo({ left: slides[cur].offsetLeft - track.offsetLeft, behavior: 'smooth' });
  }
  if (n > 1) {
    car.querySelector('.car-prev').addEventListener('click', function () { go(cur - 1); });
    car.querySelector('.car-next').addEventListener('click', function () { go(cur + 1); });
    var t;
    track.addEventListener('scroll', function () {
      clearTimeout(t);
      t = setTimeout(function () {
        cur = Math.round(track.scrollLeft / track.clientWidth);
        if (count) count.textContent = (cur + 1) + ' / ' + n;
      }, 60);
    });
  }

  // просмотр на весь экран
  var lb = document.createElement('div');
  lb.className = 'lb';
  lb.hidden = true;
  lb.setAttribute('role', 'dialog');
  lb.setAttribute('aria-modal', 'true');
  lb.setAttribute('aria-label', 'Просмотр фото');
  lb.innerHTML = '<img alt="">' +
    '<button class="lb-close" type="button" aria-label="Закрыть">×</button>' +
    (n > 1 ? '<button class="lb-prev" type="button" aria-label="Предыдущее фото">‹</button>' +
      '<button class="lb-next" type="button" aria-label="Следующее фото">›</button>' +
      '<span class="lb-count"></span>' : '');
  document.body.appendChild(lb);
  var img = lb.querySelector('img');
  var lc = lb.querySelector('.lb-count');
  var li = 0;
  function show(i) {
    li = (i + n) % n;
    var s = slides[li].querySelector('img');
    img.src = s.currentSrc || s.src;
    img.alt = s.alt;
    if (lc) lc.textContent = (li + 1) + ' / ' + n;
  }
  function open(i) { show(i); lb.hidden = false; document.body.style.overflow = 'hidden'; lb.querySelector('.lb-close').focus(); }
  function close() { lb.hidden = true; document.body.style.overflow = ''; go(li); slides[li].focus({ preventScroll: true }); }
  slides.forEach(function (b, i) { b.addEventListener('click', function () { open(i); }); });
  lb.querySelector('.lb-close').addEventListener('click', close);
  lb.addEventListener('click', function (e) { if (e.target === lb) close(); });
  if (n > 1) {
    lb.querySelector('.lb-prev').addEventListener('click', function () { show(li - 1); });
    lb.querySelector('.lb-next').addEventListener('click', function () { show(li + 1); });
  }
  document.addEventListener('keydown', function (e) {
    if (lb.hidden) return;
    if (e.key === 'Escape') close();
    else if (e.key === 'ArrowLeft' && n > 1) show(li - 1);
    else if (e.key === 'ArrowRight' && n > 1) show(li + 1);
  });
  // свайп в просмотре
  var x0 = null;
  lb.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; }, { passive: true });
  lb.addEventListener('touchend', function (e) {
    if (x0 === null || n < 2) return;
    var dx = e.changedTouches[0].clientX - x0;
    if (Math.abs(dx) > 50) show(li + (dx < 0 ? 1 : -1));
    x0 = null;
  });
})();
