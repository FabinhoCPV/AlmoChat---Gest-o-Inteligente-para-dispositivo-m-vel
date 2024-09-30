$(document).ready(function() {
    $('#loginBtn').click(function() {
        const username = $('#username').val();
        const password = $('#password').val();
        
        $.post('/login', { username: username, password: password }, function(data) {
            if (data.success) {
                alert('Login bem-sucedido!');
                $('#component-search').show();
            } else {
                alert('Usuário ou senha incorretos. Tente novamente.');
            }
        });
    });

    $('#searchBtn').click(function() {
        const componente = $('#component-name').val();
        
        $.post('/buscar_componente', { componente: componente }, function(data) {
            if (data.found) {
                $('#search-result').html(`Componente encontrado: ${data.nome}, Quantidade: ${data.quantidade}`);
                $('#search-result').show();
            } else {
                $('#search-result').html('Componente não encontrado.');
                $('#search-result').show();
            }
        });
    });
});
