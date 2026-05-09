// api/yorumlar/[yorumId].js
// PUT    /api/yorumlar/5   → yorumu düzenle
// DELETE /api/yorumlar/5   → yorumu sil
// POST   /api/yorumlar/5/begen → beğen (query: action=begen)
const { initDB } = require("../_db");

module.exports = async (req, res) => {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "PUT,DELETE,POST,OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type, x-admin-token");
  if (req.method === "OPTIONS") return res.status(200).end();

  const yorumId = Number(req.query.yorumId);
  const db = await initDB();

  // ── VOTE (upvote/downvote) ───────────────────────────────
  if (req.method === "POST" && req.query.action === "vote") {
    const { userId, tip } = req.body;
    if (!userId?.trim()) return res.status(400).json({ hata: "userId zorunludur" });
    if (tip !== 1 && tip !== -1) return res.status(400).json({ hata: "tip 1 veya -1 olmalı" });
    try {
      // Daha önce oy verdiyse güncelle, yoksa ekle
      await db.query(
        `INSERT INTO votes (yorum_id, user_id, tip) VALUES ($1,$2,$3)
         ON CONFLICT (yorum_id, user_id) DO UPDATE SET tip = EXCLUDED.tip`,
        [yorumId, userId.trim(), tip]
      );
      // Güncel sayıları döndür
      const votes = await db.query(
        `SELECT tip, COUNT(*)::INT AS sayi FROM votes WHERE yorum_id=$1 GROUP BY tip`,
        [yorumId]
      );
      const upvotes   = votes.rows.find(r => r.tip ===  1)?.sayi || 0;
      const downvotes = votes.rows.find(r => r.tip === -1)?.sayi || 0;
      return res.json({ upvotes, downvotes });
    } catch (e) { return res.status(500).json({ hata: e.message }); }
  }

  // ── YANIT ────────────────────────────────────────────────
  if (req.method === "POST" && req.query.action === "yanit") {
    const adminToken = req.headers["x-admin-token"];
    if (adminToken !== "fienix1905gs")
      return res.status(403).json({ hata: "Yanıt sadece admin tarafından yapılabilir" });
    const { metin } = req.body;
    if (!metin?.trim()) return res.status(400).json({ hata: "Metin boş olamaz" });
    try {
      const check = await db.query("SELECT id FROM yorumlar WHERE id=$1", [yorumId]);
      if (!check.rows.length) return res.status(404).json({ hata: "Yorum bulunamadı" });
      const { rows } = await db.query(
        `INSERT INTO yanitlar (yorum_id, user_id, metin) VALUES ($1,$2,$3)
         RETURNING id, user_id AS "userId", metin, tarih`,
        [yorumId, "fienix", metin.trim()]
      );
      return res.status(201).json(rows[0]);
    } catch (e) { return res.status(500).json({ hata: e.message }); }
  }

  // ── BEĞEN ─────────────────────────────────────────────────
  if (req.method === "POST" && req.query.action === "begen") {
    try {
      const { rows } = await db.query(
        "UPDATE yorumlar SET begeniler=begeniler+1 WHERE id=$1 RETURNING begeniler AS beg",
        [yorumId]
      );
      if (!rows.length) return res.status(404).json({ hata: "Yorum bulunamadı" });
      return res.json(rows[0]);
    } catch (e) { return res.status(500).json({ hata: e.message }); }
  }

  // ── DÜZENLE ───────────────────────────────────────────────
  if (req.method === "PUT") {
    const { userId, metin } = req.body;
    if (!metin?.trim()) return res.status(400).json({ hata: "Metin boş olamaz" });
    try {
      const check = await db.query("SELECT user_id FROM yorumlar WHERE id=$1", [yorumId]);
      if (!check.rows.length) return res.status(404).json({ hata: "Yorum bulunamadı" });
      if (check.rows[0].user_id !== userId)
        return res.status(403).json({ hata: "Bu yorumu düzenleme yetkiniz yok" });

      const { rows } = await db.query(
        `UPDATE yorumlar SET metin=$1, guncelleme=NOW()
         WHERE id=$2 RETURNING id, film_id AS "filmId", user_id AS "userId", metin, tarih, guncelleme`,
        [metin.trim(), yorumId]
      );
      return res.json(rows[0]);
    } catch (e) { return res.status(500).json({ hata: e.message }); }
  }

  // ── SİL ──────────────────────────────────────────────────
  if (req.method === "DELETE") {
    const { userId } = req.body;
    const adminToken = req.headers["x-admin-token"];
    const isAdmin = adminToken === "fienix1905gs";
    try {
      const check = await db.query("SELECT user_id FROM yorumlar WHERE id=$1", [yorumId]);
      if (!check.rows.length) return res.status(404).json({ hata: "Yorum bulunamadı" });
      if (!isAdmin && check.rows[0].user_id !== userId)
        return res.status(403).json({ hata: "Bu yorumu silme yetkiniz yok" });

      await db.query("DELETE FROM yorumlar WHERE id=$1", [yorumId]);
      return res.json({ mesaj: "Yorum silindi" });
    } catch (e) { return res.status(500).json({ hata: e.message }); }
  }

  res.status(405).end();
};
