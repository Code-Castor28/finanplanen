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
})();
