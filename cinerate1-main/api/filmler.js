// api/filmler.js  →  GET /api/filmler
const { initDB } = require("./_db");

module.exports = async (req, res) => {
  res.setHeader("Access-Control-Allow-Origin", "*");
  if (req.method !== "GET") return res.status(405).end();

  try {
    const db = await initDB();
    const { rows } = await db.query(`
      SELECT f.*,
        ROUND(AVG(p.puan)::NUMERIC, 1)  AS "ortalamaPuan",
        COUNT(DISTINCT p.id)::INT        AS "toplamOy",
        COUNT(DISTINCT y.id)::INT        AS "toplamYorum"
      FROM filmler f
      LEFT JOIN puanlar  p ON p.film_id = f.id
      LEFT JOIN yorumlar y ON y.film_id = f.id
      GROUP BY f.id ORDER BY f.id
    `);
    res.json(rows);
  } catch (e) {
    res.status(500).json({ hata: e.message });
  }
};
