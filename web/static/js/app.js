document.addEventListener('DOMContentLoaded', function() {
    clearSensitiveFields();
    initTabs();
    initNL2SQL();
    initVectorDB();
    initStats();
    initAuth();
    checkAuthStatus();
    
    // 监听CSV列选择变化
    const csvColumnSelect = document.getElementById('csv-column');
    if (csvColumnSelect) {
        csvColumnSelect.addEventListener('change', function() {
            const selectedColumn = this.value;
            if (selectedColumn && window.csvContent) {
                const documents = parseCSVContent(window.csvContent, selectedColumn);
                document.getElementById('documents').value = documents.join('\n');
            }
        });
    }
});

function initStats() {
    // 从本地存储加载统计数据
    const queries = localStorage.getItem('total-queries') || 0;
    const vectors = localStorage.getItem('total-vectors') || 0;
    
    document.getElementById('total-queries').textContent = queries;
    document.getElementById('total-vectors').textContent = vectors;
}

function updateStats(type, increment = 1) {
    if (type === 'queries') {
        const current = parseInt(localStorage.getItem('total-queries') || 0);
        const newCount = current + increment;
        localStorage.setItem('total-queries', newCount);
        document.getElementById('total-queries').textContent = newCount;
    } else if (type === 'vectors') {
        const current = parseInt(localStorage.getItem('total-vectors') || 0);
        const newCount = current + increment;
        localStorage.setItem('total-vectors', newCount);
        document.getElementById('total-vectors').textContent = newCount;
    }
}

function clearSensitiveFields() {
    document.getElementById('api-key').value = '';
    document.getElementById('db-host').value = 'localhost';
    document.getElementById('db-port').value = '3306';
    document.getElementById('db-user').value = '';
    document.getElementById('db-password').value = '';
    document.getElementById('db-name').value = '';
    document.getElementById('db-table').value = '';
    
    document.getElementById('documents').value = '';
    document.getElementById('file-name').textContent = '';
    document.getElementById('sql-output').textContent = '';
    document.getElementById('query-result').innerHTML = '';
    document.getElementById('optimization-tips').innerHTML = '';
    document.getElementById('search-result').innerHTML = '';
}

function initTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    const clearBtn = document.getElementById('clear-all');
    
    tabBtns.forEach(btn => {
        if (btn.id === 'clear-all') {
            btn.addEventListener('click', function() {
                if (confirm('确定要清除所有敏感数据和输入内容吗？')) {
                    clearSensitiveFields();
                    alert('数据已清除！');
                }
            });
        } else {
            btn.addEventListener('click', function() {
                const tabId = this.dataset.tab;
                
                tabBtns.forEach(b => b.classList.remove('active'));
                tabContents.forEach(c => c.classList.remove('active'));
                
                this.classList.add('active');
                document.getElementById(tabId).classList.add('active');
            });
        }
    });
}

function initNL2SQL() {
    const generateBtn = document.getElementById('generate-sql');
    const executeBtn = document.getElementById('execute-sql');
    const viewTableBtn = document.getElementById('view-table');
    const viewChartBtn = document.getElementById('view-chart');
    
    generateBtn.addEventListener('click', generateSQL);
    executeBtn.addEventListener('click', executeSQL);
    
    if (viewTableBtn) {
        viewTableBtn.addEventListener('click', function() {
            if (currentQueryResult && currentQueryResult.length > 0) {
                displayQueryResult(currentQueryResult);
            }
        });
    }
    
    if (viewChartBtn) {
        viewChartBtn.addEventListener('click', displayChart);
    }
}

async function generateSQL() {
    const nlQueryEl = document.getElementById('nl-query');
    const generateBtn = document.getElementById('generate-sql');
    const sqlOutputEl = document.getElementById('sql-output');
    const optimizationTipsEl = document.getElementById('optimization-tips');
    const llmTypeEl = document.getElementById('llm-type');
    const apiKeyEl = document.getElementById('api-key');
    const optimizeCheckbox = document.getElementById('optimize-query');
    
    if (!nlQueryEl || !generateBtn || !sqlOutputEl || !optimizationTipsEl || !llmTypeEl || !apiKeyEl) {
        showNotification('页面元素缺失，请刷新页面', 'error');
        return;
    }
    
    const nlQuery = nlQueryEl.value.trim();
    if (!nlQuery) {
        showNotification('请输入自然语言查询', 'error');
        return;
    }
    
    const originalText = generateBtn.textContent;
    generateBtn.disabled = true;
    generateBtn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg> 生成中...';
    
    try {
        const response = await fetch('/api/nl2sql/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query: nlQuery,
                llm_type: llmTypeEl.value,
                api_key: apiKeyEl.value,
                optimize: optimizeCheckbox ? optimizeCheckbox.checked : false
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || `请求失败: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            sqlOutputEl.textContent = data.sql;
            optimizationTipsEl.innerHTML = data.optimization_tips 
                ? `<ul>${data.optimization_tips.map(tip => `<li>${tip}</li>`).join('')}</ul>` 
                : '暂无优化建议 (勾选"优化查询"可启用优化)';
            
            // 更新统计信息
            updateStats('queries');
            showNotification('SQL生成成功！', 'success');
        } else {
            const errorMessage = data.error || '未知错误';
            showNotification('生成SQL失败: ' + errorMessage, 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification(`生成SQL失败: ${error.message}`, 'error');
    } finally {
        generateBtn.disabled = false;
        generateBtn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg> 生成SQL';
    }
}

async function executeSQL() {
    const sqlOutputEl = document.getElementById('sql-output');
    const executeBtn = document.getElementById('execute-sql');
    
    if (!sqlOutputEl || !executeBtn) {
        showNotification('页面元素缺失，请刷新页面', 'error');
        return;
    }
    
    const sqlOutput = sqlOutputEl.textContent.trim();
    if (!sqlOutput) {
        showNotification('请先生成SQL', 'error');
        return;
    }
    
    const originalText = executeBtn.textContent;
    executeBtn.disabled = true;
    executeBtn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg> 执行中...';
    
    try {
        const response = await fetch('/api/nl2sql/execute', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                sql: sqlOutput
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || `请求失败: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            displayQueryResult(data.result);
            showNotification('SQL执行成功！', 'success');
        } else {
            const errorMessage = data.error || '未知错误';
            showNotification('执行SQL失败: ' + errorMessage, 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification(`执行SQL失败: ${error.message}`, 'error');
    } finally {
        executeBtn.disabled = false;
        executeBtn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"></path></svg> 执行SQL';
    }
}

let currentQueryResult = [];

function displayQueryResult(result) {
    const container = document.getElementById('query-result');
    const chartContainer = document.getElementById('chart-container');
    
    if (!container) {
        alert('查询结果容器元素不存在，请刷新页面');
        return;
    }
    
    // 存储当前查询结果
    currentQueryResult = result;
    
    if (!result || result.length === 0) {
        container.innerHTML = '<p>查询结果为空</p>';
        chartContainer.style.display = 'none';
        return;
    }
    
    const keys = Object.keys(result[0]);
    let html = '<table><thead><tr>';
    
    keys.forEach(key => {
        html += `<th>${key}</th>`;
    });
    
    html += '</tr></thead><tbody>';
    
    result.forEach(row => {
        html += '<tr>';
        keys.forEach(key => {
            html += `<td>${row[key]}</td>`;
        });
        html += '</tr>';
    });
    
    html += '</tbody></table>';
    container.innerHTML = html;
    
    // 显示表格，隐藏图表
    container.style.display = 'block';
    chartContainer.style.display = 'none';
}

function displayChart() {
    const container = document.getElementById('query-result');
    const chartContainer = document.getElementById('chart-container');
    const canvas = document.getElementById('result-chart');
    
    if (!container || !chartContainer || !canvas) {
        alert('页面元素缺失，请刷新页面');
        return;
    }
    
    if (!currentQueryResult || currentQueryResult.length === 0) {
        alert('没有数据可显示');
        return;
    }
    
    const keys = Object.keys(currentQueryResult[0]);
    
    // 简单的图表类型选择逻辑
    let chartType = 'bar';
    let labels = [];
    let data = [];
    let backgroundColor = [];
    
    // 尝试找到适合作为标签的列（字符串类型）和适合作为数据的列（数字类型）
    let labelKey = keys[0];
    let dataKey = keys[1];
    
    // 检查数据类型
    const firstRow = currentQueryResult[0];
    for (let key of keys) {
        if (typeof firstRow[key] === 'string' && !isNaN(Date.parse(firstRow[key]))) {
            labelKey = key;
        } else if (typeof firstRow[key] === 'number') {
            dataKey = key;
        }
    }
    
    // 准备数据
    currentQueryResult.forEach(row => {
        labels.push(row[labelKey]);
        data.push(row[dataKey]);
        // 生成随机颜色
        const color = `rgba(${Math.floor(Math.random() * 255)}, ${Math.floor(Math.random() * 255)}, ${Math.floor(Math.random() * 255)}, 0.7)`;
        backgroundColor.push(color);
    });
    
    // 销毁旧图表
    if (window.resultChart) {
        window.resultChart.destroy();
    }
    
    // 创建新图表
    window.resultChart = new Chart(canvas, {
        type: chartType,
        data: {
            labels: labels,
            datasets: [{
                label: dataKey,
                data: data,
                backgroundColor: backgroundColor,
                borderColor: backgroundColor.map(color => color.replace('0.7', '1')),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: `数据可视化: ${labelKey} vs ${dataKey}`
                },
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
    
    // 显示图表，隐藏表格
    container.style.display = 'none';
    chartContainer.style.display = 'block';
    chartContainer.style.height = '400px';
}

function initVectorDB() {
    const buildIndexBtn = document.getElementById('build-index');
    const searchBtn = document.getElementById('search-vector');
    const fileUpload = document.getElementById('file-upload');
    const importDbBtn = document.getElementById('import-db');
    const exploreDbsBtn = document.getElementById('explore-dbs');
    const exploreTablesBtn = document.getElementById('explore-tables');
    
    buildIndexBtn.addEventListener('click', buildIndex);
    searchBtn.addEventListener('click', searchVector);
    fileUpload.addEventListener('change', handleFileUpload);
    importDbBtn.addEventListener('click', importFromDatabase);
    exploreDbsBtn.addEventListener('click', exploreDatabases);
    exploreTablesBtn.addEventListener('click', exploreTables);
}

function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    const fileNameEl = document.getElementById('file-name');
    const csvOptionsDiv = document.getElementById('csv-options');
    const csvColumnSelect = document.getElementById('csv-column');
    const documentsEl = document.getElementById('documents');
    
    if (!fileNameEl || !csvOptionsDiv || !csvColumnSelect || !documentsEl) {
        alert('页面元素缺失，请刷新页面');
        return;
    }
    
    fileNameEl.textContent = file.name;
    
    const reader = new FileReader();
    reader.onload = function(e) {
        const content = e.target.result;
        
        // 检查是否是CSV文件
        if (file.name.endsWith('.csv')) {
            // 解析CSV文件，显示列选择
            const lines = content.split('\n').filter(line => line.trim());
            if (lines.length > 0) {
                const headers = parseCSVLine(lines[0]);
                
                // 填充列选择下拉框
                csvColumnSelect.innerHTML = '<option value="">请选择</option>';
                headers.forEach(header => {
                    csvColumnSelect.innerHTML += `<option value="${header}">${header}</option>`;
                });
                
                csvOptionsDiv.style.display = 'block';
                
                // 保存完整内容供后续处理
                window.csvContent = content;
                window.csvHeaders = headers;
            }
        } else {
            // 不是CSV文件，直接显示
            csvOptionsDiv.style.display = 'none';
            documentsEl.value = content;
        }
    };
    reader.readAsText(file);
}

function parseCSVLine(line) {
    const result = [];
    let current = '';
    let inQuotes = false;
    
    for (let i = 0; i < line.length; i++) {
        const char = line[i];
        
        if (char === '"') {
            inQuotes = !inQuotes;
        } else if (char === ',' && !inQuotes) {
            result.push(current.trim());
            current = '';
        } else {
            current += char;
        }
    }
    result.push(current.trim());
    
    return result;
}

function parseCSVContent(content, columnName) {
    const lines = content.split('\n').filter(line => line.trim());
    if (lines.length < 2) return [];
    
    const headers = parseCSVLine(lines[0]);
    const columnIndex = headers.indexOf(columnName);
    
    if (columnIndex === -1) return [];
    
    const result = [];
    for (let i = 1; i < lines.length; i++) {
        const values = parseCSVLine(lines[i]);
        if (values[columnIndex]) {
            result.push(values[columnIndex]);
        }
    }
    
    return result;
}

async function buildIndex() {
    const documentsEl = document.getElementById('documents');
    const vectorDbEl = document.getElementById('vector-db');
    const buildIndexBtn = document.getElementById('build-index');
    
    if (!documentsEl || !vectorDbEl || !buildIndexBtn) {
        alert('页面元素缺失，请刷新页面');
        return;
    }
    
    const documents = documentsEl.value.trim();
    if (!documents) {
        alert('请输入文档');
        return;
    }
    
    const docList = documents.split('\n').filter(d => d.trim());
    
    const originalText = buildIndexBtn.innerHTML;
    buildIndexBtn.disabled = true;
    buildIndexBtn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg> 构建中...';
    
    try {
        const response = await fetch('/api/vector/build', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                documents: docList,
                db_type: vectorDbEl.value
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('索引构建成功！', 'success');
            // 更新统计信息
            updateStats('vectors', docList.length);
        } else {
            const errorMessage = data.error || '未知错误';
            showNotification('构建索引失败: ' + errorMessage, 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('请求失败，请检查后端服务是否启动', 'error');
    } finally {
        buildIndexBtn.disabled = false;
        buildIndexBtn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><line x1="3" y1="9" x2="21" y2="9"></line><line x1="9" y1="21" x2="9" y2="9"></line></svg> 构建索引';
    }
}

async function searchVector() {
    const vectorQueryEl = document.getElementById('vector-query');
    const vectorDbEl = document.getElementById('vector-db');
    const searchBtn = document.getElementById('search-vector');
    
    if (!vectorQueryEl || !vectorDbEl || !searchBtn) {
        alert('页面元素缺失，请刷新页面');
        return;
    }
    
    const query = vectorQueryEl.value.trim();
    if (!query) {
        alert('请输入搜索查询');
        return;
    }
    
    const originalText = searchBtn.innerHTML;
    searchBtn.disabled = true;
    searchBtn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg> 搜索中...';
    
    try {
        const response = await fetch('/api/vector/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query: query,
                db_type: vectorDbEl.value
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displaySearchResult(data.results);
        } else {
            const errorMessage = data.error || '未知错误';
            showNotification('搜索失败: ' + errorMessage, 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('请求失败，请检查后端服务是否启动', 'error');
    } finally {
        searchBtn.disabled = false;
        searchBtn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg> 搜索';
    }
}

async function importFromDatabase() {
    const hostEl = document.getElementById('db-host');
    const portEl = document.getElementById('db-port');
    const userEl = document.getElementById('db-user');
    const passwordEl = document.getElementById('db-password');
    const databaseEl = document.getElementById('db-name');
    const tableEl = document.getElementById('db-table');
    const vectorTypeEl = document.getElementById('db-vector-type');
    const importDbBtn = document.getElementById('import-db');
    
    if (!hostEl || !portEl || !userEl || !passwordEl || !databaseEl || !tableEl || !vectorTypeEl || !importDbBtn) {
        alert('页面元素缺失，请刷新页面');
        return;
    }
    
    const host = hostEl.value.trim();
    const port = portEl.value;
    const user = userEl.value.trim();
    const password = passwordEl.value;
    const database = databaseEl.value.trim();
    const table = tableEl.value.trim();
    const vectorType = vectorTypeEl.value;
    
    if (!user || !database || !table) {
        alert('请填写必要的数据库连接信息');
        return;
    }
    
    const originalText = importDbBtn.innerHTML;
    importDbBtn.disabled = true;
    importDbBtn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg> 导入中...';
    
    try {
        const response = await fetch('/api/vector/import-db', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                host: host,
                port: parseInt(port),
                user: user,
                password: password,
                database: database,
                table: table,
                columns: [],
                vector_db_type: vectorType
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification(data.message, 'success');
            // 更新统计信息
            updateStats('vectors', data.document_count || 0);
        } else {
            const errorMessage = data.error || '未知错误';
            showNotification('导入失败: ' + errorMessage, 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('请求失败，请检查后端服务是否启动', 'error');
    } finally {
        importDbBtn.disabled = false;
        importDbBtn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg> 从数据库导入';
    }
}

async function exploreDatabases() {
    const hostEl = document.getElementById('db-host');
    const portEl = document.getElementById('db-port');
    const userEl = document.getElementById('db-user');
    const passwordEl = document.getElementById('db-password');
    const dbNameEl = document.getElementById('db-name');
    const dbTableEl = document.getElementById('db-table');
    const exploreDbsBtn = document.getElementById('explore-dbs');
    
    if (!hostEl || !portEl || !userEl || !passwordEl || !dbNameEl || !dbTableEl || !exploreDbsBtn) {
        alert('页面元素缺失，请刷新页面');
        return;
    }
    
    const host = hostEl.value.trim();
    const port = portEl.value;
    const user = userEl.value.trim();
    const password = passwordEl.value;
    
    if (!user) {
        alert('请填写数据库用户名');
        return;
    }
    
    const originalText = exploreDbsBtn.innerHTML;
    exploreDbsBtn.disabled = true;
    exploreDbsBtn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg> 探索中...';
    
    try {
        const response = await fetch('/api/vector/explore-db', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                host: host,
                port: parseInt(port),
                user: user,
                password: password
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayExploreResult('数据库列表', data.databases, (db) => {
                dbNameEl.value = db;
                dbTableEl.value = '';
            });
        } else {
            const errorMessage = data.error || '未知错误';
            showNotification('探索失败: ' + errorMessage, 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('请求失败，请检查后端服务是否启动', 'error');
    } finally {
        exploreDbsBtn.disabled = false;
        exploreDbsBtn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg> 探索数据库';
    }
}

async function exploreTables() {
    const hostEl = document.getElementById('db-host');
    const portEl = document.getElementById('db-port');
    const userEl = document.getElementById('db-user');
    const passwordEl = document.getElementById('db-password');
    const databaseEl = document.getElementById('db-name');
    const dbTableEl = document.getElementById('db-table');
    const exploreTablesBtn = document.getElementById('explore-tables');
    
    if (!hostEl || !portEl || !userEl || !passwordEl || !databaseEl || !dbTableEl || !exploreTablesBtn) {
        alert('页面元素缺失，请刷新页面');
        return;
    }
    
    const host = hostEl.value.trim();
    const port = portEl.value;
    const user = userEl.value.trim();
    const password = passwordEl.value;
    const database = databaseEl.value.trim();
    
    if (!user || !database) {
        alert('请填写数据库用户名和数据库名称');
        return;
    }
    
    const originalText = exploreTablesBtn.innerHTML;
    exploreTablesBtn.disabled = true;
    exploreTablesBtn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg> 探索中...';
    
    try {
        const response = await fetch('/api/vector/explore-db', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                host: host,
                port: parseInt(port),
                user: user,
                password: password,
                database: database
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayExploreResult('表列表', data.tables, (table) => {
                dbTableEl.value = table;
            });
        } else {
            const errorMessage = data.error || '未知错误';
            showNotification('探索失败: ' + errorMessage, 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('请求失败，请检查后端服务是否启动', 'error');
    } finally {
        exploreTablesBtn.disabled = false;
        exploreTablesBtn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="6" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line><line x1="6" y1="12" x2="18" y2="12"></line></svg> 探索表';
    }
}

function displayExploreResult(title, items, clickHandler) {
    const resultDiv = document.getElementById('db-explore-result');
    
    if (!resultDiv) {
        alert('结果容器元素不存在，请刷新页面');
        return;
    }
    
    if (!items || items.length === 0) {
        resultDiv.innerHTML = `<h4>${title}</h4><p>未找到任何${title}</p>`;
        return;
    }
    
    let html = `<h4>${title}</h4><ul>`;
    items.forEach(item => {
        html += `<li data-value="${item}">${item}</li>`;
    });
    html += '</ul>';
    
    resultDiv.innerHTML = html;
    
    // 添加点击事件
    if (clickHandler) {
        const listItems = resultDiv.querySelectorAll('li');
        listItems.forEach((item, index) => {
            item.addEventListener('click', () => clickHandler(items[index]));
        });
    }
}

function displaySearchResult(results) {
    const container = document.getElementById('search-result');
    
    if (!container) {
        alert('搜索结果容器元素不存在，请刷新页面');
        return;
    }
    
    if (!results || results.length === 0) {
        container.innerHTML = '<p>未找到相关结果</p>';
        return;
    }
    
    let html = '<div style="display: flex; flex-direction: column; gap: 15px;">';
    
    results.forEach((result, index) => {
        html += `
            <div style="padding: 15px; background: white; border-radius: 8px; border: 1px solid #dee2e6; transition: all 0.3s ease; cursor: pointer;">
                <div style="font-weight: 600; color: #667eea; margin-bottom: 8px;">
                    结果 ${index + 1} (相似度: ${(result.score * 100).toFixed(2)}%)
                </div>
                <div>${result.document}</div>
            </div>
        `;
    });
    
    html += '</div>';
    container.innerHTML = html;
    
    // 添加悬停效果
    const resultItems = container.querySelectorAll('div[style*="padding: 15px"]');
    resultItems.forEach(item => {
        item.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
            this.style.boxShadow = '0 4px 12px rgba(102, 126, 234, 0.2)';
        });
        item.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = 'none';
        });
    });
}

function togglePassword(id) {
    const input = document.getElementById(id);
    const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
    input.setAttribute('type', type);
}

function copyToClipboard(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        let text = '';
        if (element.tagName === 'PRE') {
            text = element.textContent;
        } else {
            text = element.innerText;
        }
        
        navigator.clipboard.writeText(text).then(function() {
            showNotification('已复制到剪贴板', 'success');
        }, function(err) {
            console.error('复制失败:', err);
            showNotification('复制失败，请手动复制', 'error');
        });
    }
}

function showNotification(message, type = 'info', duration = 3000) {
    // 创建通知元素
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    
    // 添加图标
    let icon = '';
    if (type === 'success') {
        icon = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>';
    } else if (type === 'error') {
        icon = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>';
    } else {
        icon = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>';
    }
    
    notification.innerHTML = `${icon} ${message}`;
    
    // 添加样式
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.padding = '15px 20px';
    notification.style.borderRadius = '8px';
    notification.style.color = 'white';
    notification.style.fontWeight = '600';
    notification.style.zIndex = '10000';
    notification.style.animation = 'slideIn 0.3s ease';
    notification.style.display = 'flex';
    notification.style.alignItems = 'center';
    notification.style.gap = '10px';
    
    // 设置不同类型的背景色
    if (type === 'success') {
        notification.style.backgroundColor = '#11998e';
    } else if (type === 'error') {
        notification.style.backgroundColor = '#ff6b6b';
    } else {
        notification.style.backgroundColor = '#667eea';
    }
    
    // 添加到页面
    document.body.appendChild(notification);
    
    // 一段时间后移除
    setTimeout(function() {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(function() {
            document.body.removeChild(notification);
        }, 300);
    }, duration);
}

// 添加动画样式
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

function showAboutModal() {
    document.getElementById('about-modal').style.display = 'block';
}

function showHelpModal() {
    document.getElementById('help-modal').style.display = 'block';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// 点击模态框外部关闭
window.onclick = function(event) {
    const modals = document.getElementsByClassName('modal');
    for (let i = 0; i < modals.length; i++) {
        if (event.target == modals[i]) {
            modals[i].style.display = 'none';
        }
    }
};

// 认证相关函数
function initAuth() {
    const loginBtn = document.getElementById('login-btn');
    const logoutBtn = document.getElementById('logout-btn');
    const submitLoginBtn = document.getElementById('submit-login');
    
    if (loginBtn) {
        loginBtn.addEventListener('click', function() {
            document.getElementById('login-modal').style.display = 'block';
        });
    }
    
    if (logoutBtn) {
        logoutBtn.addEventListener('click', logout);
    }
    
    if (submitLoginBtn) {
        submitLoginBtn.addEventListener('click', login);
    }
}

function checkAuthStatus() {
    const token = localStorage.getItem('auth_token');
    const userInfo = document.getElementById('user-info');
    const loginBtn = document.getElementById('login-btn');
    const usernameDisplay = document.getElementById('username-display');
    
    if (token) {
        // 验证token是否有效
        fetch('/api/auth/me', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error('Token invalid');
            }
        })
        .then(data => {
            if (userInfo && loginBtn && usernameDisplay) {
                userInfo.style.display = 'flex';
                loginBtn.style.display = 'none';
                usernameDisplay.textContent = data.username;
            }
        })
        .catch(() => {
            localStorage.removeItem('auth_token');
            if (userInfo && loginBtn) {
                userInfo.style.display = 'none';
                loginBtn.style.display = 'block';
            }
        });
    } else {
        if (userInfo && loginBtn) {
            userInfo.style.display = 'none';
            loginBtn.style.display = 'block';
        }
    }
}

async function login() {
    const usernameEl = document.getElementById('login-username');
    const passwordEl = document.getElementById('login-password');
    const submitLoginBtn = document.getElementById('submit-login');
    
    if (!usernameEl || !passwordEl || !submitLoginBtn) {
        alert('页面元素缺失，请刷新页面');
        return;
    }
    
    const username = usernameEl.value.trim();
    const password = passwordEl.value;
    
    if (!username || !password) {
        alert('请输入用户名和密码');
        return;
    }
    
    const originalText = submitLoginBtn.textContent;
    submitLoginBtn.disabled = true;
    submitLoginBtn.textContent = '登录中...';
    
    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username: username,
                password: password
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            localStorage.setItem('auth_token', data.access_token);
            showNotification('登录成功！', 'success');
            closeModal('login-modal');
            checkAuthStatus();
        } else {
            const errorMessage = data.detail || '登录失败';
            showNotification('登录失败: ' + errorMessage, 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('请求失败，请检查后端服务是否启动', 'error');
    } finally {
        submitLoginBtn.disabled = false;
        submitLoginBtn.textContent = originalText;
    }
}

function logout() {
    localStorage.removeItem('auth_token');
    checkAuthStatus();
    showNotification('已登出', 'info');
}

function getAuthHeaders() {
    const token = localStorage.getItem('auth_token');
    if (token) {
        return {
            'Authorization': `Bearer ${token}`
        };
    }
    return {};
}