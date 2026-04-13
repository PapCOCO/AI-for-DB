document.addEventListener('DOMContentLoaded', function() {
    clearSensitiveFields();
    initTabs();
    initNL2SQL();
    initVectorDB();
    
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

function clearSensitiveFields() {
    document.getElementById('api-key').value = '';
    document.getElementById('db-host').value = 'localhost';
    document.getElementById('db-port').value = '3306';
    document.getElementById('db-user').value = '';
    document.getElementById('db-password').value = '';
    document.getElementById('db-name').value = '';
    document.getElementById('db-table').value = '';
    document.getElementById('db-column').value = '';
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
    
    generateBtn.addEventListener('click', generateSQL);
    executeBtn.addEventListener('click', executeSQL);
}

async function generateSQL() {
    const nlQuery = document.getElementById('nl-query').value.trim();
    if (!nlQuery) {
        alert('请输入自然语言查询');
        return;
    }
    
    try {
        const response = await fetch('/api/nl2sql/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query: nlQuery,
                llm_type: document.getElementById('llm-type').value,
                api_key: document.getElementById('api-key').value
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('sql-output').textContent = data.sql;
            document.getElementById('optimization-tips').innerHTML = data.optimization_tips 
                ? `<ul>${data.optimization_tips.map(tip => `<li>${tip}</li>`).join('')}</ul>` 
                : '暂无优化建议';
        } else {
            alert('生成SQL失败: ' + data.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('请求失败，请检查后端服务是否启动');
    }
}

async function executeSQL() {
    const sqlOutput = document.getElementById('sql-output').textContent.trim();
    if (!sqlOutput) {
        alert('请先生成SQL');
        return;
    }
    
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
        
        const data = await response.json();
        
        if (data.success) {
            displayQueryResult(data.result);
        } else {
            alert('执行SQL失败: ' + data.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('请求失败，请检查后端服务是否启动');
    }
}

function displayQueryResult(result) {
    const container = document.getElementById('query-result');
    
    if (!result || result.length === 0) {
        container.innerHTML = '<p>查询结果为空</p>';
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
}

function initVectorDB() {
    const buildIndexBtn = document.getElementById('build-index');
    const searchBtn = document.getElementById('search-vector');
    const fileUpload = document.getElementById('file-upload');
    const importDbBtn = document.getElementById('import-db');
    const exploreDbsBtn = document.getElementById('explore-dbs');
    const exploreTablesBtn = document.getElementById('explore-tables');
    const exploreColumnsBtn = document.getElementById('explore-columns');
    
    buildIndexBtn.addEventListener('click', buildIndex);
    searchBtn.addEventListener('click', searchVector);
    fileUpload.addEventListener('change', handleFileUpload);
    importDbBtn.addEventListener('click', importFromDatabase);
    exploreDbsBtn.addEventListener('click', exploreDatabases);
    exploreTablesBtn.addEventListener('click', exploreTables);
    exploreColumnsBtn.addEventListener('click', exploreColumns);
}

function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    document.getElementById('file-name').textContent = file.name;
    const csvOptionsDiv = document.getElementById('csv-options');
    const csvColumnSelect = document.getElementById('csv-column');
    
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
            document.getElementById('documents').value = content;
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
    const documents = document.getElementById('documents').value.trim();
    if (!documents) {
        alert('请输入文档');
        return;
    }
    
    const docList = documents.split('\n').filter(d => d.trim());
    
    try {
        const response = await fetch('/api/vector/build', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                documents: docList,
                db_type: document.getElementById('vector-db').value
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('索引构建成功！');
        } else {
            alert('构建索引失败: ' + data.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('请求失败，请检查后端服务是否启动');
    }
}

async function searchVector() {
    const query = document.getElementById('vector-query').value.trim();
    if (!query) {
        alert('请输入搜索查询');
        return;
    }
    
    try {
        const response = await fetch('/api/vector/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query: query,
                db_type: document.getElementById('vector-db').value
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displaySearchResult(data.results);
        } else {
            alert('搜索失败: ' + data.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('请求失败，请检查后端服务是否启动');
    }
}

async function importFromDatabase() {
    const host = document.getElementById('db-host').value.trim();
    const port = document.getElementById('db-port').value;
    const user = document.getElementById('db-user').value.trim();
    const password = document.getElementById('db-password').value;
    const database = document.getElementById('db-name').value.trim();
    const table = document.getElementById('db-table').value.trim();
    const vectorType = document.getElementById('db-vector-type').value;
    const importAllColumns = document.getElementById('import-all-columns').checked;
    
    // 获取选中的列
    let columns = [];
    const columnsSelect = document.getElementById('db-columns');
    for (let i = 0; i < columnsSelect.options.length; i++) {
        if (columnsSelect.options[i].selected) {
            columns.push(columnsSelect.options[i].value);
        }
    }
    
    if (!user || !database || !table) {
        alert('请填写必要的数据库连接信息');
        return;
    }
    
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
                columns: importAllColumns ? [] : columns,
                vector_db_type: vectorType
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert(data.message);
        } else {
            alert('导入失败: ' + data.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('请求失败，请检查后端服务是否启动');
    }
}

async function exploreDatabases() {
    const host = document.getElementById('db-host').value.trim();
    const port = document.getElementById('db-port').value;
    const user = document.getElementById('db-user').value.trim();
    const password = document.getElementById('db-password').value;
    
    if (!user) {
        alert('请填写数据库用户名');
        return;
    }
    
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
                document.getElementById('db-name').value = db;
                document.getElementById('db-table').value = '';
                document.getElementById('db-column').value = '';
            });
        } else {
            alert('探索失败: ' + data.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('请求失败，请检查后端服务是否启动');
    }
}

async function exploreTables() {
    const host = document.getElementById('db-host').value.trim();
    const port = document.getElementById('db-port').value;
    const user = document.getElementById('db-user').value.trim();
    const password = document.getElementById('db-password').value;
    const database = document.getElementById('db-name').value.trim();
    
    if (!user || !database) {
        alert('请填写数据库用户名和数据库名称');
        return;
    }
    
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
                document.getElementById('db-table').value = table;
                document.getElementById('db-column').value = '';
            });
        } else {
            alert('探索失败: ' + data.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('请求失败，请检查后端服务是否启动');
    }
}

async function exploreColumns() {
    const host = document.getElementById('db-host').value.trim();
    const port = document.getElementById('db-port').value;
    const user = document.getElementById('db-user').value.trim();
    const password = document.getElementById('db-password').value;
    const database = document.getElementById('db-name').value.trim();
    const table = document.getElementById('db-table').value.trim();
    
    if (!user || !database || !table) {
        alert('请填写数据库用户名、数据库名称和表名');
        return;
    }
    
    try {
        const response = await fetch('/api/vector/explore-table', {
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
                table: table
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // 填充列选择下拉框
            const columnsSelect = document.getElementById('db-columns');
            columnsSelect.innerHTML = '';
            data.columns.forEach(column => {
                const option = document.createElement('option');
                option.value = column.name;
                option.textContent = `${column.name} (${column.type})`;
                columnsSelect.appendChild(option);
            });
            
            displayColumnsResult('列列表', data.columns, (column) => {
                // 找到对应的选项并选中
                const columnsSelect = document.getElementById('db-columns');
                for (let i = 0; i < columnsSelect.options.length; i++) {
                    if (columnsSelect.options[i].value === column) {
                        columnsSelect.options[i].selected = true;
                        break;
                    }
                }
            });
        } else {
            alert('探索失败: ' + data.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('请求失败，请检查后端服务是否启动');
    }
}

function displayExploreResult(title, items, clickHandler) {
    const resultDiv = document.getElementById('db-explore-result');
    
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

function displayColumnsResult(title, columns, clickHandler) {
    const resultDiv = document.getElementById('db-explore-result');
    
    if (!columns || columns.length === 0) {
        resultDiv.innerHTML = `<h4>${title}</h4><p>未找到任何列</p>`;
        return;
    }
    
    let html = `<h4>${title}</h4><table>`;
    html += '<thead><tr><th>列名</th><th>类型</th><th>允许空</th><th>键</th></tr></thead><tbody>';
    
    columns.forEach(column => {
        html += `<tr data-column="${column.name}">
            <td>${column.name}</td>
            <td>${column.type}</td>
            <td>${column.null ? '是' : '否'}</td>
            <td>${column.key}</td>
        </tr>`;
    });
    
    html += '</tbody></table>';
    resultDiv.innerHTML = html;
    
    // 添加点击事件
    if (clickHandler) {
        const tableRows = resultDiv.querySelectorAll('tbody tr');
        tableRows.forEach((row, index) => {
            row.addEventListener('click', () => clickHandler(columns[index].name));
        });
    }
}

function displaySearchResult(results) {
    const container = document.getElementById('search-result');
    
    if (!results || results.length === 0) {
        container.innerHTML = '<p>未找到相关结果</p>';
        return;
    }
    
    let html = '<div style="display: flex; flex-direction: column; gap: 15px;">';
    
    results.forEach((result, index) => {
        html += `
            <div style="padding: 15px; background: white; border-radius: 8px; border: 1px solid #dee2e6;">
                <div style="font-weight: 600; color: #667eea; margin-bottom: 8px;">
                    结果 ${index + 1} (相似度: ${(result.score * 100).toFixed(2)}%)
                </div>
                <div>${result.document}</div>
            </div>
        `;
    });
    
    html += '</div>';
    container.innerHTML = html;
}