/ EDDIGUDHA AI — Netlify serverless AI endpoint
// Set AI_PROVIDER to "openai" or "gemini" and AI_API_KEY in Netlify environment variables.
// Never put your API key in index.html, script.js, or any public file.

exports.handler = async (event) => {
  const headers = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "POST, OPTIONS"
  };

  if (event.httpMethod === "OPTIONS") return { statusCode: 204, headers, body: "" };
  if (event.httpMethod !== "POST") return { statusCode: 405, headers, body: JSON.stringify({ error: "Method not allowed." }) };

  const provider = (process.env.AI_PROVIDER || "").toLowerCase();
  const apiKey = process.env.AI_API_KEY;
  if (!apiKey || !["openai", "gemini"].includes(provider)) {
    return {
      statusCode: 503, headers,
      body: JSON.stringify({ error: "AI setup is not complete yet. Add AI_PROVIDER (openai or gemini) and AI_API_KEY in Netlify environment variables." })
    };
  }

  try {
    const payload = JSON.parse(event.body || "{}");
    const messages = Array.isArray(payload.messages) ? payload.messages.slice(-20) : [];
    if (!messages.length) return { statusCode: 400, headers, body: JSON.stringify({ error: "Please enter a message." }) };

    let reply = "";
    if (provider === "openai") {
      const upstream = await fetch("https://api.openai.com/v1/chat/completions", {
        method: "POST",
        headers: { "Authorization": `Bearer ${apiKey}`, "Content-Type": "application/json" },
        body: JSON.stringify({
          model: process.env.AI_MODEL || "gpt-4o-mini",
          messages: [
            { role: "system", content: "You are EDDIGUDHA AI, a helpful, clear and friendly assistant. Be accurate and concise." },
            ...messages.map(m => ({ role: m.role === "assistant" ? "assistant" : "user", content: String(m.content || "").slice(0, 8000) }))
          ],
          temperature: 0.7
        })
      });
      const result = await upstream.json();
      if (!upstream.ok) throw new Error(result.error?.message || `OpenAI returned status ${upstream.status}`);
      reply = result.choices?.[0]?.message?.content || "";
    } else {
      const contents = messages.map(m => ({
        role: m.role === "assistant" ? "model" : "user",
        parts: [{ text: String(m.content || "").slice(0, 8000) }]
      }));
      const model = process.env.AI_MODEL || "gemini-2.0-flash";
      const upstream = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${encodeURIComponent(apiKey)}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          systemInstruction: { parts: [{ text: "You are EDDIGUDHA AI, a helpful, clear and friendly assistant. Be accurate and concise." }] },
          contents,
          generationConfig: { temperature: 0.7, maxOutputTokens: 1200 }
        })
      });
      const result = await upstream.json();
      if (!upstream.ok) throw new Error(result.error?.message || `Gemini returned status ${upstream.status}`);
      reply = result.candidates?.[0]?.content?.parts?.map(p => p.text || "").join("") || "";
    }

    return { statusCode: 200, headers, body: JSON.stringify({ reply }) };
  } catch (error) {
    return { statusCode: 500, headers, body: JSON.stringify({ error: error.message || "Unexpected server error." }) };
  }
};
