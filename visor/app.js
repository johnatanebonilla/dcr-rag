document.addEventListener('DOMContentLoaded', () => {
    // UI Elements
    const listContainer = document.getElementById('lemaList');
    const searchInput = document.getElementById('searchInput');
    const alphabetNav = document.getElementById('alphabetNav');
    const viewerContent = document.getElementById('viewerContent');
    const welcomeScreen = document.getElementById('welcomeScreen');
    
    // Toggles
    const checkDef = document.getElementById('checkDef');
    const checkSub = document.getElementById('checkSub');
    const checkEje = document.getElementById('checkEje');
    
    // Output Areas
    const outLema = document.getElementById('outLema');
    const outCat = document.getElementById('outCat');
    const outIntro = document.getElementById('outIntro');
    const outAcepciones = document.getElementById('outAcepciones');
    const outEtim = document.getElementById('outEtim');
    
    // Modal
    const modal = document.getElementById('jsonModal');
    const jsonRawPre = document.getElementById('jsonRaw');
    const btnRaw = document.getElementById('viewRawJson');
    const btnCloseModal = document.getElementById('closeModal');
    
    let fullIndex = [];
    let currentData = null;
    let currentFilter = '';
    let selectedLetter = null;

    // 1. Initial Load
    fetch('../json_semantico/index_db.json')
        .then(r => r.json())
        .then(data => {
            fullIndex = data;
            document.getElementById('viewerStats').innerText = `Base de datos cargada: ${fullIndex.length} lemas procesados.`;
            createAlphabetNav();
            renderList(fullIndex);
        })
        .catch(e => {
            listContainer.innerHTML = '<div class="loading">Error al cargar index_db.json. Verifique la carpeta /json_semantico.</div>';
        });

    // 2. Alphabet Navigation
    function createAlphabetNav() {
        const alphabet = "ABCDEFGHIJKLMNÑOPQRSTUVWXYZ".split("");
        alphabet.forEach(letter => {
            const btn = document.createElement('button');
            btn.className = 'alpha-btn';
            btn.innerText = letter;
            btn.onclick = () => filterByLetter(letter, btn);
            alphabetNav.appendChild(btn);
        });
    }

    function filterByLetter(letter, btn) {
        if (selectedLetter === letter) {
            selectedLetter = null;
            btn.classList.remove('active');
            renderList(fullIndex);
        } else {
            document.querySelectorAll('.alpha-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            selectedLetter = letter;
            searchInput.value = '';
            
            const filtered = fullIndex.filter(item => {
                const first = prepareLema(item.lema).charAt(0).toUpperCase();
                return first === letter;
            });
            renderList(filtered);
        }
    }

    function prepareLema(text) {
        return text.replace(/^[«"¿¡\[\(-]+/, '').normalize("NFD").replace(/[\u0300-\u036f]/g, "");
    }

    // 3. List Rendering
    function renderList(items) {
        listContainer.innerHTML = '';
        // Limit to 300 items for performance
        const visible = items.slice(0, 300);
        
        visible.forEach(item => {
            const el = document.createElement('div');
            el.className = 'list-item';
            el.innerHTML = item.lema;
            el.onclick = () => {
                document.querySelectorAll('.list-item').forEach(i => i.classList.remove('selected'));
                el.classList.add('selected');
                loadEntry(item.file);
            };
            listContainer.appendChild(el);
        });
        
        if (items.length === 0) {
            listContainer.innerHTML = '<div class="loading">No hay resultados.</div>';
        }
    }

    // 4. Search
    searchInput.addEventListener('input', (e) => {
        const val = e.target.value.toLowerCase();
        selectedLetter = null;
        document.querySelectorAll('.alpha-btn').forEach(b => b.classList.remove('active'));
        
        const filtered = fullIndex.filter(i => i.lema.toLowerCase().includes(val));
        renderList(filtered);
    });

    // 5. Load & Render Entry
    function loadEntry(file) {
        fetch(`../json_semantico/${file}`)
            .then(r => r.json())
            .then(data => {
                currentData = data;
                renderEntry(data);
                welcomeScreen.classList.add('hidden');
                viewerContent.classList.remove('hidden');
            });
    }

    function renderEntry(data) {
        outLema.innerHTML = data.lema;
        outLema.className = 'dcr-lema';
        
        outCat.innerText = data.categoria_gramatical;
        outCat.className = 'dcr-categoria';
        
        outIntro.innerHTML = data.introduccion;
        outIntro.className = 'dcr-introduccion';
        
        outAcepciones.innerHTML = '';
        outAcepciones.className = 'dcr-acepciones-lista';
        data.acepciones.forEach(acep => {
            const div = document.createElement('div');
            div.className = 'dcr-acepcion-item acepcion-item';
            
            let html = `
                <div class="acepcion-head">
                    <span class="dcr-marcador-acepcion acepcion-num">${acep.id}</span>
                    <div class="dcr-definicion acepcion-text">${acep.definicion}</div>
                </div>
                ${renderCitas(acep.ejemplos_citas)}
            `;
            
            if (acep.subacepciones && acep.subacepciones.length > 0) {
                html += `<div class="dcr-subacepciones-lista sub-list">`;
                acep.subacepciones.forEach(sub => {
                    html += `
                        <div class="dcr-subacepcion-item sub-item">
                            <div class="acepcion-head">
                                <span class="dcr-marcador-acepcion sub-num">${sub.id_marcador}</span>
                                <div class="dcr-definicion sub-text">${sub.definicion}</div>
                            </div>
                            ${renderCitas(sub.ejemplos_citas)}
                        </div>
                    `;
                });
                html += `</div>`;
            }
            
            div.innerHTML = html;
            outAcepciones.appendChild(div);
        });

        // Add Construction / Sintaxis if present
        if (data.construccion_sintactica) {
            const constrDiv = document.createElement('div');
            constrDiv.className = 'extra-section construction-box';
            constrDiv.innerHTML = `<h3>Construcciones Sintácticas</h3><div class="section-content">${data.construccion_sintactica}</div>`;
            outAcepciones.appendChild(constrDiv);
        }
        
        outEtim.innerHTML = data.etimologia ? `<div class="extra-section etim-box dcr-etimologia">${data.etimologia}</div>` : '';
    }

    function renderCitas(citas) {
        if (!citas || citas.length === 0) return '';
        let html = '<div class="examples-grid">';
        citas.forEach(c => {
            html += `
                <div class="dcr-cita-contenedor example-card">
                    <span class="dcr-cita-texto quote">${c.texto_cita}</span>
                    <div class="meta">
                        <span class="dcr-autor author">${c.autor || ''}</span>
                        ${c.referencia_obra ? `<span class="dcr-referencia cite">${c.referencia_obra}</span>` : ''}
                    </div>
                </div>
            `;
        });
        html += '</div>';
        return html;
    }

    // 6. View Control Toggles
    const updateToggles = () => {
        viewerContent.classList.toggle('hide-def', !checkDef.checked);
        viewerContent.classList.toggle('hide-sub', !checkSub.checked);
        viewerContent.classList.toggle('hide-eje', !checkEje.checked);
    };
    
    checkDef.onchange = updateToggles;
    checkSub.onchange = updateToggles;
    checkEje.onchange = updateToggles;

    // 7. JSON Modal
    btnRaw.onclick = () => {
        jsonRawPre.innerText = JSON.stringify(currentData, null, 2);
        modal.classList.remove('hidden');
    };
    btnCloseModal.onclick = () => modal.classList.add('hidden');
    modal.onclick = (e) => { if(e.target === modal) modal.classList.add('hidden'); };
});
