document.addEventListener('DOMContentLoaded', () => {
    const sidebarNav = document.getElementById('sidebarNav');
    const searchInput = document.getElementById('searchInput');
    const challengeDetails = document.getElementById('challengeDetails');

    let units = [];
    let challenges = [];
    let qbank = [];
    let state = {
        unitMap: new Map(),
        challengeMap: new Map(),
        groupedChallenges: new Map(),
        qbankMap: new Map()
    };

    async function fetchData() {
        try {
            const [unitsRes, challengesRes] = await Promise.all([
                fetch('/units.json').catch(() => null),
                fetch('/challenges.json').catch(() => null)
            ]);

            if (unitsRes) units = await unitsRes.json();
            if (challengesRes) challenges = await challengesRes.json();

            if (!Array.isArray(units)) units = units.data || units.units || [];
            if (!Array.isArray(challenges)) challenges = challenges.data || challenges.challenges || [];

            processAndRenderData();
        } catch (error) {
            console.error('Error fetching data:', error);
            sidebarNav.innerHTML = `<div class="loading" style="color: var(--text-danger)">Error loading data. Check console.</div>`;
        }
    }

    function processAndRenderData() {
        units.forEach(unit => {
            state.unitMap.set(unit._id || unit.id, unit);
        });

        challenges.forEach(challenge => {
            state.challengeMap.set(challenge._id || challenge.id, challenge);
            const unitId = challenge.unitId || challenge.unit_id || challenge.unit; 
            
            if (!state.groupedChallenges.has(unitId)) {
                state.groupedChallenges.set(unitId, []);
            }
            state.groupedChallenges.get(unitId).push(challenge);
        });

        for (let [unitId, unitChallenges] of state.groupedChallenges.entries()) {
            unitChallenges.sort((a, b) => {
                const stepA = parseInt(a.step || a.order || 0);
                const stepB = parseInt(b.step || b.order || 0);
                return stepA - stepB;
            });
        }

        renderSidebar();
    }

    function renderSidebar(searchTerm = '') {
        sidebarNav.innerHTML = '';
        
        if (state.groupedChallenges.size === 0) {
            sidebarNav.innerHTML = '<div class="loading">No challenges found.</div>';
            return;
        }

        const term = searchTerm.toLowerCase();
        let hasResults = false;

        const sortedUnitIds = Array.from(state.groupedChallenges.keys()).sort((a, b) => {
            const idA = parseInt(a) || 0;
            const idB = parseInt(b) || 0;
            return idA - idB;
        });

        sortedUnitIds.forEach(unitId => {
            const idNum = parseInt(unitId);
            // Skip units 0 through 2000
            if (!isNaN(idNum) && idNum >= 0 && idNum <= 2000) {
                return;
            }

            const unit = state.unitMap.get(unitId) || { name: `Unit ${unitId}`, id: unitId };
            const unitChallenges = state.groupedChallenges.get(unitId) || [];
            
            const filteredChallenges = unitChallenges.filter(c => {
                const cName = (c.name || c.title || '').toLowerCase();
                const uName = (unit.name || '').toLowerCase();
                return cName.includes(term) || uName.includes(term);
            });

            if (filteredChallenges.length > 0) {
                hasResults = true;
                const groupEl = document.createElement('div');
                groupEl.className = 'unit-group';
                if (term) groupEl.classList.add('expanded');
                
                const unitName = unit.name || `Unit ${unitId}`;
                const unitIdDisplay = unit.id !== undefined ? unit.id : unitId;

                groupEl.innerHTML = `
                    <div class="unit-header">
                        <div class="unit-title">Unit ${unitIdDisplay} : ${unitName}</div>
                        <div class="unit-icon">▼</div>
                    </div>
                    <div class="challenge-list">
                        ${filteredChallenges.map(c => {
                            const cName = c.name || c.title || `Challenge ${c.id || c._id}`;
                            const cId = c._id || c.id;
                            const stepStr = c.step ? `Step ${c.step} - ` : '';
                            return `<div class="challenge-item" data-id="${cId}">${stepStr}${cName}</div>`;
                        }).join('')}
                    </div>
                `;

                const header = groupEl.querySelector('.unit-header');
                header.addEventListener('click', () => {
                    groupEl.classList.toggle('expanded');
                });

                const items = groupEl.querySelectorAll('.challenge-item');
                items.forEach(item => {
                    item.addEventListener('click', () => {
                        document.querySelectorAll('.challenge-item').forEach(el => el.classList.remove('active'));
                        item.classList.add('active');
                        
                        const challengeId = item.getAttribute('data-id');
                        const challenge = state.challengeMap.get(challengeId) || state.challengeMap.get(parseInt(challengeId));
                        
                        if (challenge) {
                            renderChallenge(challenge, unit);
                        }
                    });
                });

                sidebarNav.appendChild(groupEl);
            }
        });

        if (!hasResults) {
            sidebarNav.innerHTML = '<div class="loading">No matches found.</div>';
        }
    }

    async function renderChallenge(challenge, unit) {
        const unitName = unit.name || `Unit ${unit.id || 'Unknown'}`;
        const unitIdStr = unit.id !== undefined ? unit.id : '';
        const chName = challenge.name || challenge.title || `Challenge ${challenge.id || ''}`;
        const chStep = challenge.step || challenge.order || '';
        
        let pdfLink = '';
        const uId = parseInt(unit.id || challenge.unit || 0);
        
        if (uId >= 2001 && uId <= 2017) pdfLink = '/notes/foundation.pdf';
        else if (uId >= 3031 && uId <= 3039) pdfLink = '/notes/advanced_1.pdf';
        else if (uId >= 3040 && uId <= 3047) pdfLink = '/notes/advanced_2.pdf';
        else if (uId >= 3048 && uId <= 3054) pdfLink = '/notes/advanced_3.pdf';

        let notesHtml = pdfLink ? `<a href="${pdfLink}" target="_blank" class="notes-btn">📚 View Notes</a>` : '';

        let html = `
            <div class="challenge-header">
                <div class="meta-unit">Unit: ${unitIdStr} - ${unitName}</div>
                <div style="display: flex; justify-content: space-between; align-items: center; gap: 16px; flex-wrap: wrap;">
                    <h1 class="challenge-title" style="margin:0;">Challenge: ${chStep ? chStep + ' - ' : ''}${chName}</h1>
                    ${notesHtml}
                </div>
                ${chStep ? `<div class="step-badge">You are on Step ${chStep}</div>` : ''}
            </div>
            <div id="stepsContainer"><div class="loading">Loading details...</div></div>
        `;

        challengeDetails.className = 'challenge-details';
        challengeDetails.innerHTML = html;

        try {
            const id = challenge.uid || challenge.id || challenge._id;
            const res = await fetch(`/qbank/${id}.json`);
            const stepsContainer = document.getElementById('stepsContainer');

            if (res.ok) {
                const qb = await res.json();
                if (qb && qb.steps && qb.steps.length > 0) {
                    let stepsHtml = '';
                    qb.steps.forEach((step, idx) => {
                        const diffBadge = step.difficulty ? `<span style="background:var(--text-accent); color:var(--bg-dark); padding:2px 8px; border-radius:4px; font-size:12px; margin-left:8px; text-transform:uppercase">${step.difficulty}</span>` : '';
                        stepsHtml += `
                        <div class="glass-card" style="margin-bottom: 24px;">
                            <div class="section-title">Step ${step.step_id || (idx + 1)} ${diffBadge}</div>
                            <div class="description-content html-rendered" style="font-size:15px; color:var(--text-primary);">
                                ${step.description || 'No description provided.'}
                            </div>
                        </div>
                        `;
                    });
                    stepsContainer.innerHTML = stepsHtml;
                } else {
                    stepsContainer.innerHTML = `<div class="glass-card"><div class="description-content">No steps found for this challenge.</div></div>`;
                }
            } else {
                stepsContainer.innerHTML = `<div class="glass-card"><div class="description-content">No extra details found (or question bank not loaded).</div></div>`;
            }
        } catch (err) {
            document.getElementById('stepsContainer').innerHTML = `<div class="glass-card"><div class="description-content">Error loading details.</div></div>`;
        }
    }

    function formatText(text) {
        if (!text) return '';
        return text
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/\n/g, '<br>');
    }

    searchInput.addEventListener('input', (e) => {
        renderSidebar(e.target.value);
    });

    fetchData();
});
