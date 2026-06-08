/* ===== Side Toggle ===== */
document.querySelectorAll('#sideToggle .toggle-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('#sideToggle .toggle-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById('side').value = btn.dataset.value;
  });
});

/* ===== Order Type — show/hide price fields ===== */
const orderTypeEl   = document.getElementById('order_type');
const priceGroup    = document.getElementById('priceGroup');
const stopPriceGroup = document.getElementById('stopPriceGroup');

function updatePriceFields() {
  const t = orderTypeEl.value;
  priceGroup.style.display     = t === 'LIMIT'       ? 'flex' : 'none';
  stopPriceGroup.style.display = t === 'STOP_MARKET' ? 'flex' : 'none';
}
orderTypeEl.addEventListener('change', updatePriceFields);
updatePriceFields();

/* ===== Order History ===== */
const history = [];

function addToHistory(res) {
  history.unshift(res);
  const historyCard  = document.getElementById('historyCard');
  const historyCount = document.getElementById('historyCount');
  const tbody        = document.getElementById('historyBody');
  historyCard.style.display = 'block';
  historyCount.textContent  = history.length;

  const d = res;
  const avgPrice = d.avgPrice && parseFloat(d.avgPrice) > 0 ? parseFloat(d.avgPrice).toFixed(2) : d.price || '—';
  const status   = (d.status || '').toUpperCase();
  const statusCls = status === 'FILLED' ? 'status-filled-cell' : status === 'NEW' ? 'status-new-cell' : '';

  const tr = document.createElement('tr');
  tr.innerHTML = `
    <td>${d.orderId || '—'}</td>
    <td>${d.symbol  || '—'}</td>
    <td class="${d.side === 'BUY' ? 'side-buy' : 'side-sell'}">${d.side || '—'}</td>
    <td>${d.type || '—'}</td>
    <td>${d.origQty || '—'}</td>
    <td>${avgPrice}</td>
    <td class="${statusCls}">${status || '—'}</td>
  `;
  tbody.prepend(tr);
}

/* ===== Render Response ===== */
function renderSuccess(data) {
  const card = document.getElementById('responseCard');
  const title = document.getElementById('responseTitle');
  const body  = document.getElementById('responseBody');

  card.className = 'card response-success';
  title.textContent = 'Order Result';
  card.style.display = 'block';

  const avgPrice = data.avgPrice && parseFloat(data.avgPrice) > 0
    ? parseFloat(data.avgPrice).toFixed(2)
    : data.price || 'N/A';

  const statusCls = data.status === 'FILLED' ? 'status-filled' : data.status === 'NEW' ? 'status-new' : '';

  body.innerHTML = `
    <div class="result-badge badge-success">&#10003; Order Placed Successfully</div>
    <div class="result-grid">
      <div class="result-item"><span class="result-label">Order ID</span>     <span class="result-value">${data.orderId}</span></div>
      <div class="result-item"><span class="result-label">Symbol</span>       <span class="result-value">${data.symbol}</span></div>
      <div class="result-item"><span class="result-label">Side</span>         <span class="result-value ${data.side === 'BUY' ? 'side-buy' : 'side-sell'}">${data.side}</span></div>
      <div class="result-item"><span class="result-label">Type</span>         <span class="result-value">${data.type}</span></div>
      <div class="result-item"><span class="result-label">Status</span>       <span class="result-value ${statusCls}">${data.status}</span></div>
      <div class="result-item"><span class="result-label">Orig Qty</span>     <span class="result-value">${data.origQty}</span></div>
      <div class="result-item"><span class="result-label">Executed Qty</span> <span class="result-value">${data.executedQty}</span></div>
      <div class="result-item"><span class="result-label">Avg Price</span>    <span class="result-value">${avgPrice}</span></div>
      <div class="result-item"><span class="result-label">Client Order</span> <span class="result-value">${data.clientOrderId || '—'}</span></div>
      <div class="result-item"><span class="result-label">Time in Force</span><span class="result-value">${data.timeInForce || '—'}</span></div>
    </div>`;

  addToHistory(data);
  card.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function renderError(message) {
  const card  = document.getElementById('responseCard');
  const title = document.getElementById('responseTitle');
  const body  = document.getElementById('responseBody');

  card.className = 'card response-error';
  title.textContent = 'Order Failed';
  card.style.display = 'block';

  body.innerHTML = `
    <div class="result-badge badge-error">&#10007; Error</div>
    <p class="result-value error-text">${message}</p>`;

  card.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

/* ===== Form Submit ===== */
document.getElementById('orderForm').addEventListener('submit', async (e) => {
  e.preventDefault();

  const btn     = document.getElementById('submitBtn');
  const btnText = document.getElementById('btnText');
  const spinner = document.getElementById('btnSpinner');

  btn.disabled = true;
  btnText.textContent = 'Placing...';
  spinner.style.display = 'inline-block';

  const payload = {
    symbol:     document.getElementById('symbol').value.trim().toUpperCase(),
    side:       document.getElementById('side').value,
    order_type: document.getElementById('order_type').value,
    quantity:   parseFloat(document.getElementById('quantity').value),
    price:      parseFloat(document.getElementById('price').value) || null,
    stop_price: parseFloat(document.getElementById('stop_price').value) || null,
  };

  try {
    const res  = await fetch('/api/order', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const json = await res.json();
    if (json.success) renderSuccess(json.data);
    else              renderError(json.error || 'Unknown error');
  } catch (err) {
    renderError('Network error: could not reach the server.');
  } finally {
    btn.disabled = false;
    btnText.textContent = 'Place Order';
    spinner.style.display = 'none';
  }
});
