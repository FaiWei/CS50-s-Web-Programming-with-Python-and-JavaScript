console.log(`user check initiated`);
document.addEventListener('DOMContentLoaded', () => {
    const request = new XMLHttpRequest();
    request.open('GET', '/usercheck');
    request.onload = () => {
        const response = JSON.parse(request.response);
        if (response.success) {
            console.log(`yai`);            
            let usercarcas = response.usercarcas;
            const nickname = response.user;
            usercarcas.querySelector('#nickname').innerHTML = nickname;
            document.querySelector('#pageswitch').innerHTML = usercarcas;
        }
        else {
            const contents = response.input
            document.querySelector('#pageswitch').innerHTML = contents;
        }
    } 
    request.send();
});

