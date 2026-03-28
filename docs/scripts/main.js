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
    const path = window.location.pathname.split('/').pop() || 'index.html';
    links.forEach(a => {
      const href = a.getAttribute('href').split('/').pop();
      if(href === path){
        a.classList.add('active');
        a.setAttribute('aria-current','page');
      }
    });
  }catch(e){/* ignore in simple environments */}
});
