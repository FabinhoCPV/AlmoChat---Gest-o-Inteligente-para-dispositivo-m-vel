document.getElementById('loginForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const formData = new FormData(this);
    
    fetch('/login', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById('loginForm').style.display = 'none';
            document.getElementById('componentSection').style.display = 'block';
        } else {
            alert('Login falhou. Tente novamente.');
        }
    });
});

document.getElementById('searchForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const formData = new FormData(this);
    
    fetch('/buscar_componente', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.found) {
            document.getElementById('componenteInfo').style.display = 'block';
            document.getElementById('componenteNome').innerText = `Nome: ${data.nome}`;
            document.getElementById('componenteQuantidade').innerText = `Quantidade em estoque: ${data.quantidade}`;
            document.getElementById('componentePosicao').innerText = `Posição: ${data.Posicao || 'Não especificada'}`; // Exibe a posição
            document.getElementById('componenteInfo').dataset.componenteId = data.id;
        } else {
            alert('Componente não encontrado.');
        }
    });
});

document.getElementById('adicionarBtn').addEventListener('click', function() {
    atualizarComponente('adicionar');
});

document.getElementById('retirarBtn').addEventListener('click', function() {
    atualizarComponente('retirar');
});

function atualizarComponente(acao) {
    const quantidade = document.getElementById('quantidade').value;
    const componenteId = document.getElementById('componenteInfo').dataset.componenteId;
    const usuario = document.getElementById('username').value;  // Usando o nome do usuário autenticado
    
    if (!quantidade || quantidade <= 0) {
        alert('Por favor, insira uma quantidade válida.');
        return;
    }

    const formData = new FormData();
    formData.append('id', componenteId);
    formData.append('quantidade', quantidade);
    formData.append('acao', acao);
    formData.append('usuario', usuario);

    fetch('/atualizar_componente', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById('componenteQuantidade').innerText = `Quantidade em estoque: ${data.nova_quantidade}`;
            document.getElementById('componentePosicao').innerText = `Posição: ${data.posicao || 'Não especificada'}`; // Atualiza a posição
            alert('Operação realizada com sucesso!');
        } else {
            alert(data.message || 'Erro ao atualizar o componente.');
        }
    });
}
