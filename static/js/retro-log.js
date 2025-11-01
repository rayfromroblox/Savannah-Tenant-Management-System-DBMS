// Minimal helper for auto-scrolling a retro log <pre>
(function(){
  function autoScroll(container){
    if (!container) return;
    container.scrollTop = container.scrollHeight;
  }

  // Optional API to append lines
  window.retroLog = {
    append: function(selector, text){
      var el = document.querySelector(selector);
      if (!el) return;
      var pre = el.tagName.toLowerCase() === 'pre' ? el : el.querySelector('pre');
      if (!pre) return;
      pre.appendChild(document.createTextNode((pre.textContent ? '\n' : '') + String(text)));
      autoScroll(el);
    },
    scrollToBottom: function(selector){
      var el = document.querySelector(selector);
      autoScroll(el);
    }
  };
})();


