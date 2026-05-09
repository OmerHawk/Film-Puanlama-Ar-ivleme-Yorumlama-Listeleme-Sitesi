// api/filmler/[filmId]/puanla.js
// POST /api/filmler/101/puanla
const { initDB } = require("../../_db");

module.exports = async (req, res) => {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "POST,OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
  if (req.method === "OPTIONS") return res.status(200).end();
  if (req.method !== "POST") return res.status(405).end();

  const filmId = Number(req.query.filmId);
  const { userId, puan } = req.body;

  if (!userId?.trim() || puan == null)
    return res.status(400).json({ hata: "userId ve puan zorunludur" });
  if (userId.trim() === "fienix" && req.headers["x-admin-token"] !== "fienix1905gs")
    return res.status(403).json({ hata: "Bu kullanıcı adı ayrılmıştır." });
  if (puan < 0.5 || puan > 5)
    return res.status(400).json({ hata: "Puan 0.5-5 arasında olmalıdır" });

  try {
    const db = await initDB();
    const film = await db.query("SELECT id FROM filmler WHERE id=$1", [filmId]);
    if (!film.rows.length) return res.status(404).json({ hata: "Film bulunamadı" });

    const { rows } = await db.query(
      `INSERT INTO puanlar (film_id, user_id, puan)
       VALUES ($1,$2,$3)
       ON CONFLICT (film_id, user_id) DO UPDATE SET puan = EXCLUDED.puan
       RETURNING id, film_id AS "filmId", user_id AS "userId", puan`,
      [filmId, userId.trim(), Number(puan)]
    );
    res.status(201).json(rows[0]);
  } catch (e) {
    res.status(500).json({ hata: e.message });
  }
};
