EDDIGUDHA AI — Acode + Netlify starter

FILES
- index.html: website structure
- style.css: premium black and gold design
- script.js: chat interface
- netlify/functions/chat.js: secure server-side AI connection
- netlify.toml: Netlify configuration

IMPORTANT SECURITY
Do NOT paste your API key into index.html or script.js.
The API key belongs in Netlify environment variables only.

DEPLOY USING YOUR PHONE
1. Extract this ZIP.
2. In Acode, open the extracted eddigudha-ai folder.
3. Check that index.html and netlify.toml are in the main folder, and chat.js is inside netlify/functions/.
4. Upload the complete folder contents to a GitHub repository (keep the folders).
5. In Netlify, choose Add new site > Import an existing project > GitHub.
6. Select the repository. Build command can be left blank; publish directory is ".".
7. Deploy the site.

IDENTIFY YOUR API PROVIDER FIRST
Find the service/site where you created the API key. The provider is usually named in that dashboard or in the API documentation. Do not send the key itself.
Once identified, in Netlify go to Site configuration > Environment variables and add:
- AI_PROVIDER = gemini  (if it is a Google Gemini key)
  OR
- AI_PROVIDER = openai   (if it is an OpenAI key)
- AI_API_KEY = your secret key

Optional:
- AI_MODEL = gemini-2.0-flash (Gemini default)
  OR
- AI_MODEL = gpt-4o-mini (OpenAI default)

After adding/changing variables, redeploy the site.

NOTE
This starter supports OpenAI and Google Gemini API formats. If your key comes from another provider, do not guess a setting; tell us the provider's website or API documentation URL (never the key), and the server function can be adapted.
