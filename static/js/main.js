(function(){
  'use strict';

  /* Sidebar toggle */
  var sidebar = document.getElementById('sidebar');
  var overlay = document.getElementById('sidebarOverlay');
  var hamburger = document.getElementById('hamburgerBtn');
  var mobNav = document.querySelector('.mob-nav');

  if (hamburger) {
    hamburger.addEventListener('click', function(){
      sidebar.classList.add('open');
      overlay.classList.add('show');
      if (mobNav) mobNav.style.display = 'none';
    });
  }
  if (overlay) {
    overlay.addEventListener('click', function(){
      sidebar.classList.remove('open');
      overlay.classList.remove('show');
      if (mobNav) mobNav.style.display = '';
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
        : type === 'warning' ? 'fas fa-exclamation-triangle'
        : 'fas fa-check-circle';
    }
    toastEl.className = 'toast';
    if (type) toastEl.classList.add(type);
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

  function clearIdleTimers() {
    clearTimeout(idleTimer);
    clearInterval(countdownInterval);
    if (idleModal) idleModal.classList.remove('open');
  }

  function startIdleTimer(delay) {
    clearIdleTimers();
    idleTimer = setTimeout(showIdleWarning, delay || IDLE_TIMEOUT);
  }

  function resetIdleTimer() {
    clearIdleTimers();
    startIdleTimer();
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

  function getDocHidden() {
    return document.hidden || (document.webkitHidden !== undefined && document.webkitHidden);
  }

  function onPageShow() {
    var hiddenAt = sessionStorage.getItem('idle_hidden_at');
    if (hiddenAt) {
      sessionStorage.removeItem('idle_hidden_at');
      var elapsed = Date.now() - parseInt(hiddenAt, 10);
      if (elapsed >= IDLE_TIMEOUT) {
        sessionStorage.setItem('sesion_expirada', '1');
        window.location.href = '/acceso/salir/';
        return;
      }
      startIdleTimer(Math.max(IDLE_TIMEOUT - elapsed, 10000));
    } else {
      startIdleTimer();
    }
  }

  if (window.location.pathname.indexOf('/acceso/') === -1) {
    var activityEvents = ['mousedown', 'mousemove', 'click', 'keydown', 'touchstart', 'touchend', 'focusin', 'scroll', 'wheel'];
    for (var i = 0; i < activityEvents.length; i++) {
      document.addEventListener(activityEvents[i], resetIdleTimer);
    }
    startIdleTimer();
    if (continueBtn) {
      continueBtn.addEventListener('click', resetIdleTimer);
    }

    document.addEventListener('visibilitychange', function() {
      if (getDocHidden()) {
        sessionStorage.setItem('idle_hidden_at', Date.now());
      } else {
        var hiddenAt = sessionStorage.getItem('idle_hidden_at');
        if (hiddenAt) {
          sessionStorage.removeItem('idle_hidden_at');
          var elapsed = Date.now() - parseInt(hiddenAt, 10);
          if (elapsed >= IDLE_TIMEOUT) {
            sessionStorage.setItem('sesion_expirada', '1');
            window.location.href = '/acceso/salir/';
          } else {
            startIdleTimer(Math.max(IDLE_TIMEOUT - elapsed, 10000));
          }
        }
      }
    });

    if (document.webkitHidden !== undefined) {
      document.addEventListener('webkitvisibilitychange', function() {
        if (getDocHidden()) {
          sessionStorage.setItem('idle_hidden_at', Date.now());
        } else {
          var hiddenAt = sessionStorage.getItem('idle_hidden_at');
          if (hiddenAt) {
            sessionStorage.removeItem('idle_hidden_at');
            var elapsed = Date.now() - parseInt(hiddenAt, 10);
            if (elapsed >= IDLE_TIMEOUT) {
              sessionStorage.setItem('sesion_expirada', '1');
              window.location.href = '/acceso/salir/';
            } else {
              startIdleTimer(Math.max(IDLE_TIMEOUT - elapsed, 10000));
            }
          }
        }
      });
    }

    window.addEventListener('pageshow', onPageShow);
  }

  /* Avatar dropdown toggle */
  var avatarBtn = document.getElementById('avatarBtn');
  var avatarDropdown = document.getElementById('avatarDropdown');

  if (avatarBtn && avatarDropdown) {
    avatarBtn.addEventListener('click', function(e) {
      e.stopPropagation();
      avatarDropdown.classList.toggle('show');
    });

    document.addEventListener('click', function(e) {
      if (!avatarBtn.contains(e.target) && !avatarDropdown.contains(e.target)) {
        avatarDropdown.classList.remove('show');
      }
    });

    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape') avatarDropdown.classList.remove('show');
    });
  }
})();
