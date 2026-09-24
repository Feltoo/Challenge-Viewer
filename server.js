const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = 3000;

// The Cookie from your web.thelab.id session (instructor.felix)
const SESSION_COOKIE = '';

app.use(express.static(path.join(__dirname, 'public')));

// Optional: Load question bank into memory to serve individual questions fast
let questionBank = null;
const qbPath = path.join(__dirname, 'public', 'question_bank.json');

function getQuestionBank() {
    if (questionBank) return questionBank;
    if (fs.existsSync(qbPath)) {
        try {
            const data = fs.readFileSync(qbPath, 'utf8');
            const parsed = JSON.parse(data);
            questionBank = parsed.question_bank || parsed;
            return questionBank;
        } catch (e) {
            console.error("Error parsing question_bank.json:", e);
            return null;
        }
    }
    return null;
}

// Local API to get a specific challenge's questions
app.get('/api/local/question/:id', (req, res) => {
    const qb = getQuestionBank();
    if (!qb) {
        return res.status(404).json({ error: 'Question bank not loaded.' });
    }
    const id = req.params.id;
    const challenge = qb.find(q => String(q.challenge_uid) === id || String(q.challenge_id) === id);
    if (challenge) {
        res.json(challenge);
    } else {
        res.status(404).json({ error: 'Challenge not found' });
    }
});

app.use('/api', createProxyMiddleware({
    target: 'https://web.thelab.id',
    changeOrigin: true,
    secure: false,
    onProxyReq: (proxyReq, req, res) => {
        if (SESSION_COOKIE) {
            proxyReq.setHeader('Cookie', SESSION_COOKIE);
        }
    }
}));

app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}`);
    console.log(`Open http://localhost:${PORT} in your browser.`);
});
