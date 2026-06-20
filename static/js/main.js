(function(){
  'use strict';

  /* Sidebar toggle */
  var sidebar = document.getElementById('sidebar');
  var overlay = document.getElementById('sidebarOverlay');
  var hamburger = document.getElementById('hamburgerBtn');

  if (hamburger) {
    hamburger.addEventListener('click', function(){
      sidebar.classList.add('open');
      overlay.classList.add('show');
    });
  }
  if (overlay) {
    overlay.addEventListener('click', function(){
      sidebar.classList.remove('open');
      overlay.classList.remove('show');
    });
  }

  /* Global toast */
  var toastEl = document.getElementById('toast');
  var toastMsg = document.getElementById('toastMsg');
  var toastTimer;

  window.showToast = function(msg, type){
    if (!toastEl || !toastMsg) return;
    toastMsg.textContent = msg;
    var icon = toastEl.querySelector('i');
    if (icon) {
      icon.className = type === 'error' ? 'fas fa-exclamation-circle'
        : type === 'info' ? 'fas fa-info-circle'
        : 'fas fa-check-circle';
    }
    toastEl.className = 'toast';
    void toastEl.offsetWidth;
    toastEl.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function(){ toastEl.classList.remove('show'); }, 3000);
  };
  window.toast = window.showToast;

  /* Session idle timeout — 15 min inactividad → 60s cuenta regresiva → logout */
  var IDLE_TIMEOUT = 5 * 60 * 1000;
  var COUNTDOWN = 30;
  var idleTimer, countdownInterval;
  var idleModal = document.getElementById('idle-modal');
  var countdownEl = document.getElementById('idle-countdown');
  var continueBtn = document.getElementById('idle-continue');

  function resetIdleTimer() {
    clearTimeout(idleTimer);
    clearInterval(countdownInterval);
    if (idleModal) idleModal.classList.remove('open');
    idleTimer = setTimeout(showIdleWarning, IDLE_TIMEOUT);
  }

  function showIdleWarning() {
    if (!idleModal) return;
    idleModal.classList.add('open');
    var remaining = COUNTDOWN;
    if (countdownEl) countdownEl.textContent = remaining;
    countdownInterval = setInterval(function() {
      remaining--;
      if (countdownEl) countdownEl.textContent = remaining;
      if (remaining <= 0) {
        clearInterval(countdownInterval);
        sessionStorage.setItem('sesion_expirada', '1');
        window.location.href = '/acceso/salir/';
      }
    }, 1000);
  }

  if (window.location.pathname.indexOf('/acceso/') === -1) {
    var activityEvents = ['mousedown', 'mousemove', 'click', 'keydown', 'touchstart', 'scroll', 'wheel'];
    for (var i = 0; i < activityEvents.length; i++) {
      document.addEventListener(activityEvents[i], resetIdleTimer);
    }
    resetIdleTimer();
    if (continueBtn) {
      continueBtn.addEventListener('click', resetIdleTimer);
    }

    var hiddenAt = null;
    document.addEventListener('visibilitychange', function() {
      if (document.hidden) {
        hiddenAt = Date.now();
      } else if (hiddenAt !== null) {
        var elapsed = Date.now() - hiddenAt;
        hiddenAt = null;
        if (elapsed >= IDLE_TIMEOUT) {
          sessionStorage.setItem('sesion_expirada', '1');
          window.location.href = '/acceso/salir/';
        } else {
          resetIdleTimer();
        }
      }
    });
  }
})();
