// api/filmler/[filmId]/yorumlar.js
// GET  /api/filmler/101/yorumlar  → yorumları + ortalama puanı getir
// POST /api/filmler/101/yorumlar  → yeni yorum ekle
const { initDB } = require("../../_db");

module.exports = async (req, res) => {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET,POST,OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
  if (req.method === "OPTIONS") return res.status(200).end();

  const filmId = Number(req.query.filmId);
  const db = await initDB();

  // Film var mı?
  const filmQ = await db.query("SELECT * FROM filmler WHERE id=$1", [filmId]);
  if (!filmQ.rows.length) return res.status(404).json({ hata: "Film bulunamadı" });
  const film = filmQ.rows[0];

  // ── GET ──────────────────────────────────────────────────
  if (req.method === "GET") {
    try {
      const yorumlar = await db.query(
        `SELECT id, film_id AS "filmId", user_id AS "userId",
                metin, tarih, guncelleme,
                guncelleme IS NOT NULL AS gunc,
                begeniler AS beg
         FROM yorumlar WHERE film_id=$1 ORDER BY tarih DESC`,
        [filmId]
      );
      const puan = await db.query(
        `SELECT ROUND(AVG(puan)::NUMERIC,1) AS ort, COUNT(*)::INT AS toplam
         FROM puanlar WHERE film_id=$1`,
        [filmId]
      );
      const filmPuanlari = await db.query(
        `SELECT user_id AS "userId", puan FROM puanlar WHERE film_id=$1`,
        [filmId]
      );

      // Her yorumun yanitlarini ve vote'larini getir
      const yorumlarWithReplies = await Promise.all(yorumlar.rows.map(async y => {
        const replies = await db.query(
          `SELECT id, user_id AS "userId", metin, tarih FROM yanitlar WHERE yorum_id=$1 ORDER BY tarih ASC`,
          [y.id]
        );
        const votes = await db.query(
          `SELECT tip, COUNT(*)::INT AS sayi FROM votes WHERE yorum_id=$1 GROUP BY tip`,
          [y.id]
        );
        const upvotes   = votes.rows.find(r => r.tip ===  1)?.sayi || 0;
        const downvotes = votes.rows.find(r => r.tip === -1)?.sayi || 0;
        return { ...y, yanitlar: replies.rows, upvotes, downvotes };
      }));

      return res.json({
        film,
        yorumlar     : yorumlarWithReplies,
        ortalamaPuan : puan.rows[0].ort ? Number(puan.rows[0].ort) : null,
        toplamOy     : puan.rows[0].toplam,
        filmPuanlari : filmPuanlari.rows,
      });
    } catch (e) { return res.status(500).json({ hata: e.message }); }
  }

  // ── POST ─────────────────────────────────────────────────
  if (req.method === "POST") {
    const { userId, metin } = req.body;
    if (!userId?.trim() || !metin?.trim())
      return res.status(400).json({ hata: "userId ve metin zorunludur" });
    if (userId.trim() === "fienix" && req.headers["x-admin-token"] !== "fienix1905gs")
      return res.status(403).json({ hata: "Bu kullanıcı adı ayrılmıştır." });
    if (metin.trim().length > 1000)
      return res.status(400).json({ hata: "Yorum en fazla 1000 karakter" });

    try {
      const { rows } = await db.query(
        `INSERT INTO yorumlar (film_id, user_id, metin)
         VALUES ($1,$2,$3)
         RETURNING id, film_id AS "filmId", user_id AS "userId", metin, tarih`,
        [filmId, userId.trim(), metin.trim()]
      );
      return res.status(201).json(rows[0]);
    } catch (e) { return res.status(500).json({ hata: e.message }); }
  }

  res.status(405).end();
};
