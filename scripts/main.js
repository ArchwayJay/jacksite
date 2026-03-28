// Small interactive behavior for the scaffold
document.addEventListener('DOMContentLoaded', function(){
  const btn = document.getElementById('action');
  const msg = document.getElementById('message');
  if(btn && msg){
    btn.addEventListener('click', function(){
      msg.textContent = 'You clicked the button! Nice.';
      btn.textContent = 'Clicked';
      console.log('Button clicked — message updated');
    });
  }

  // navigation toggle for small screens
  const navToggle = document.getElementById('navToggle');
  const siteNav = document.getElementById('siteNav');
  if(navToggle && siteNav){
    navToggle.addEventListener('click', function(){
      siteNav.classList.toggle('open');
      const expanded = siteNav.classList.contains('open');
      navToggle.setAttribute('aria-expanded', expanded ? 'true' : 'false');
    });
  }

  // highlight active link based on current path
  try{
    const links = document.querySelectorAll('.site-nav a');
    const normalize = (p) => {
      if(!p) return 'index.html';
      // strip query/hash
      p = p.split('?')[0].split('#')[0];
      // remove leading/trailing slashes
      p = p.replace(/^\/+|\/+$/g, '');
      if(p === '') return 'index.html';
      const parts = p.split('/');
      const last = parts[parts.length-1];
      // if last part has no extension, treat as directory and use index.html
      if(!last.includes('.')) return last + '/index.html';
      return last;
    };
    const current = (function(){
      const p = window.location.pathname;
      const n = normalize(p);
      return n.split('/').pop();
    })();
    links.forEach(a => {
      const raw = a.getAttribute('href') || '';
      const hrefNorm = (function(){
        // handle relative paths and bare names
        let h = raw.replace(/^\.\//,'');
        // if href points to a directory like 'blog' or 'blog/'
        return normalize(h).split('/').pop();
      })();
      if(hrefNorm === current){
        a.classList.add('active');
        a.setAttribute('aria-current','page');
      }
    });
  }catch(e){/* ignore in simple environments */}
});
