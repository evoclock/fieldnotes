// Move the existing table into a native modal. Never clone rows or IDs.
(() => {
  const article = document.querySelector('main > article');
  const tables = [...document.querySelectorAll('.review-table')];
  if (!article || !tables.length) return;

  const dialog = document.createElement('dialog');
  dialog.className = 'table-dialog';
  dialog.setAttribute('aria-labelledby', 'expanded-table-title');
  dialog.innerHTML = '<div class="table-dialog-bar"><h2 id="expanded-table-title">Expanded table</h2><button type="button" class="table-close">Close table</button></div><p class="table-dialog-hint">Scroll sideways for any columns outside the view.</p><div class="table-dialog-content"></div>';
  article.append(dialog);
  const content = dialog.querySelector('.table-dialog-content');
  const close = dialog.querySelector('.table-close');
  let active = null;

  for (const table of tables) {
    const button = table.querySelector('.table-expand');
    button.hidden = false;
    button.addEventListener('click', () => {
      if (active) return;
      const placeholder = document.createComment('Expanded table returns here');
      table.before(placeholder);
      active = {table, placeholder, button, overflow: document.body.style.overflow};
      content.append(table);
      button.setAttribute('aria-expanded', 'true');
      document.body.style.overflow = 'hidden';
      dialog.showModal();
      close.focus();
    });
  }

  close.addEventListener('click', () => dialog.close());
  dialog.addEventListener('close', () => {
    if (!active) return;
    const {table, placeholder, button, overflow} = active;
    placeholder.replaceWith(table);
    button.setAttribute('aria-expanded', 'false');
    document.body.style.overflow = overflow;
    active = null;
    button.focus();
  });
})();
