(function () {
  const resultBox = document.getElementById("result");

  function esc(value) {
    return String(value ?? "").replace(/[&<>"']/g, ch => ({
      "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"
    }[ch]));
  }

  function renderResult(data) {
    const allocations = (data.allocations || []).map(a => `
      <div class="allocation">
        <div><strong>${esc(a.category)}</strong><span>${esc(a.explanation)}</span></div>
        <b>₹${Number(a.amount).toLocaleString("en-IN")}</b>
      </div>`).join("");

    const recs = (data.recommendations || []).map(r => `
      <article class="recommendation">
        <div class="rec-top"><span class="pill">${esc(r.category)}</span><span>${esc(r.platform)}</span></div>
        <h3>${esc(r.name)}</h3>
        <p>${esc(r.why)}</p>
        <div class="rec-bottom">
          <strong>₹${Number(r.estimated_price).toLocaleString("en-IN")}</strong>
          ${r.url ? `<a href="${esc(r.url)}" target="_blank" rel="noopener noreferrer">Open platform →</a>` : ""}
        </div>
      </article>`).join("");

    const tips = (data.tips || []).map(t => `<li>${esc(t)}</li>`).join("");

    resultBox.innerHTML = `
      <div class="section-heading"><p class="eyebrow">YOUR PLAN</p><h2>${esc(data.title)}</h2><p class="muted">${esc(data.summary)}</p></div>
      <div class="result-grid">
        <section class="card">
          <h2>Budget allocation</h2>
          ${allocations}
          <div class="total-row"><span>Total</span><strong>₹${Number(data.budget).toLocaleString("en-IN")}</strong></div>
        </section>
        <section class="card">
          <h2>Recommendations</h2>
          ${recs}
        </section>
      </div>
      ${tips ? `<section class="card tips"><h2>Practical tips</h2><ul>${tips}</ul></section>` : ""}
      <p class="muted disclaimer">${esc(data.disclaimer)} Source: ${esc(data.source)}.</p>
    `;
    resultBox.scrollIntoView({behavior:"smooth", block:"start"});
  }

  async function submitJsonForm(form, url, payload) {
    const loading = form.querySelector(".loading");
    loading.hidden = false;
    try {
      const response = await fetch(url, {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify(payload)
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Request failed");
      renderResult(data);
    } catch (err) {
      resultBox.innerHTML = `<div class="error">${esc(err.message)}</div>`;
    } finally {
      loading.hidden = true;
    }
  }

  if (window.POCKETSMART_PAGE === "home") {
    const rooms = document.getElementById("rooms");
    const addRoom = document.getElementById("add-room");

    function addRoomRow() {
      const row = document.createElement("div");
      row.className = "room-row";
      row.innerHTML = `
        <div class="room-head"><strong>Room</strong><button type="button">Remove</button></div>
        <div class="form-grid">
          <label>Room type<input class="room-type" value="Living Room" required></label>
          <label>Quantity<input class="room-quantity" type="number" min="1" value="1" required></label>
        </div>
        <label>Items<input class="room-items" placeholder="sofa, lighting, rug"></label>`;
      row.querySelector("button").onclick = () => row.remove();
      rooms.appendChild(row);
    }
    addRoom.onclick = addRoomRow;
    addRoomRow();

    document.getElementById("home-form").addEventListener("submit", e => {
      e.preventDefault();
      const f = new FormData(e.currentTarget);
      const roomData = [...document.querySelectorAll(".room-row")].map(row => ({
        room_type: row.querySelector(".room-type").value,
        quantity: Number(row.querySelector(".room-quantity").value),
        items: row.querySelector(".room-items").value.split(",").map(x => x.trim()).filter(Boolean)
      }));
      submitJsonForm(e.currentTarget, "/generate-home", {
        budget:Number(f.get("budget")), city:f.get("city"), style:f.get("style"),
        notes:f.get("notes"), rooms:roomData
      });
    });
  }

  if (window.POCKETSMART_PAGE === "party") {
    document.getElementById("party-form").addEventListener("submit", e => {
      e.preventDefault();
      const f = new FormData(e.currentTarget);
      submitJsonForm(e.currentTarget, "/generate-party", {
        budget:Number(f.get("budget")), guest_count:Number(f.get("guest_count")),
        event_type:f.get("event_type"), venue:f.get("venue"), city:f.get("city"),
        food_preference:f.get("food_preference"), notes:f.get("notes")
      });
    });
  }

  if (window.POCKETSMART_PAGE === "jewelry") {
    document.getElementById("jewelry-form").addEventListener("submit", async e => {
      e.preventDefault();
      const form = e.currentTarget;
      const loading = form.querySelector(".loading");
      loading.hidden = false;
      try {
        const response = await fetch("/generate-jewelry", {method:"POST", body:new FormData(form)});
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || "Request failed");
        renderResult(data);
      } catch (err) {
        resultBox.innerHTML = `<div class="error">${esc(err.message)}</div>`;
      } finally {
        loading.hidden = true;
      }
    });
  }
})();
