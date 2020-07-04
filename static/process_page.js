document.addEventListener('DOMContentLoaded', () => {
    let ReadyToEmitMessage = false;         //used to allow post message in socket io
    let checkChat = false;                  //if true - chat created
    let GlobalPrevChannel;                  //used in "chosedLink" to clear css decoration

    // Onload or reload.
    const request = new XMLHttpRequest();
    request.open('GET', '/check');
    request.onload = () => {
        const response = JSON.parse(request.response);
        if (response.success) {            
            nickname = response.user;
            let helloUserDiv = document.querySelector('#helloUser');
            helloUserDiv.innerHTML += nickname + '.';
        }
        if (response.loadChannelsReady) {     
            let ExistingChannels = response.LoadExistingChannels;
            for (let i = 0; ExistingChannels[(i)] != undefined; i++) {
                createChannel(ExistingChannels[i], i);
            }
            createChat();
            console.log("reload chat, channel: " + response.ChannelID);
            checkChat = true;
            chosedLink(response.ChannelID);
            load_channel(response.ChannelID);
        } 
    } 
    request.send();
    // "load_channel" also load channel messages.
    function load_channel(channelID) {
        const request = new XMLHttpRequest();
        request.open('GET', `/${channelID}`);
        request.onload = () => {
            const response = JSON.parse(request.response);
            let messages = response.Messages;
            let channel = response.Channel;
            document.querySelector('#channel-chat').innerHTML = '';
            if (response.success) {
                let titleChannel = document.querySelector('#titleChannel');
                titleChannel.innerHTML = `Channel #${channel}`;
                for (message of messages) {
                    postMessage(message.message, message.user, message.timestamp);
                }
            }
        };
        request.send();
    }


    // Instant message exchange with public share
    let connectionTie = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
    connectionTie.on('connect', () => {
        if (document.querySelector('#createChannelButton')) {
            document.querySelector('#createChannelButton').onclick = () => {
                const ChannelName = document.querySelector('#inputChannelName').value;
                connectionTie.emit('submit channel name', {'channel_name': ChannelName});
                document.querySelector('#inputChannelName').value = '';
                return false;
            };
        }
        document.querySelector('#spam').onclick = () => {
            let counter_i = 0;
            let timerId = setInterval(function() {
                connectionTie.emit('submit message', {'user_message': ('message' + counter_i), "time_stamp": getTimestamp()});
                counter_i++;
            }, 100);
            setTimeout(() => { clearInterval(timerId); alert('stop'); }, 10000);
            return false;
        }
        document.onclick = () => {
            if (ReadyToEmitMessage == true) {
                ReadyToEmitMessage = false;
                const userMessage = document.querySelector('#inputMessage').value;
                connectionTie.emit('submit message', {'user_message': userMessage, "time_stamp": getTimestamp()});
                document.querySelector('#inputMessage').value = '';
            }
        }
    })

    // Share data with all users
    connectionTie.on('share channel name', data => {
        if (data.ChatCreated && !checkChat) {
            createChat();
            checkChat = true;
        }
        createChannel(data.ChannelNameEmit, data.ChannelID);
        chosedLink(data.ChannelID);
    });
    connectionTie.on('share user message', data => {
        postMessage(data.UserMessageEmit, data.User, data.Timestamp);
    }); 


    // "Create HTML" section
    function createChannel(name, id) {
        const li = document.createElement('li');
        const channelLink = document.createElement('a');
        channelLink.href = "";
        channelLink.classList.add("channel-link");                             
        channelLink.dataset.link = `${id}`;
        channelLink.innerHTML = `${name}`;
        li.append(channelLink);
        channelLink.onclick = dynamicLink;
        document.querySelector('#channelList').append(li);
    }
    function createChat() {
        const form = document.createElement('form');
        const fieldset = document.createElement('fieldset');
        const div = document.createElement('div');
        const div2 = document.createElement('div');
        div.classList.add("form-group"); 
        div2.classList.add("form-group"); 
        const button = document.createElement('button');
        button.id = "sendMessageButton";
        button.type = "submit";
        button.className = "btn btn-primary";
        button.innerHTML = "Send";
        button.onclick = buttonMessage;
        const input = document.createElement('input');
        input.id = "inputMessage";
        input.class = "form-control";
        input.placeholder = "Message";
        input.type = "text";
        input.autocomplete = "off";
        input.className = "form-control";
        div.append(input);
        fieldset.append(div);
        div2.append(button);
        fieldset.append(div);
        fieldset.append(div2);
        form.append(fieldset);
        document.querySelector('#message-in-chat').append(form);
    }


    // Buttons that return false and do smth.
    function dynamicLink() {
        chosedLink(this.dataset.link);
        load_channel(this.dataset.link);
        return false;
    }
    function buttonMessage() {
        ReadyToEmitMessage = true;
        return false;
    }

    // Small functions whose names speak for themselves.
    function postMessage(message, user, timestamp) {
        const li = document.createElement('li');
        li.innerHTML = `${user} (${timestamp}): ${message}`;
        document.querySelector('#channel-chat').append(li);
    }
    function getTimestamp() {
        let date = new Date();
        dateStamp = date.getHours() + ':' + date.getMinutes() + ':' + date.getSeconds();
        return dateStamp;
    }
    function chosedLink(channelNumber) {
        let link = document.querySelector(`[data-link="${channelNumber}"]`)
        link.style.fontWeight = 'bold';
        if (GlobalPrevChannel != undefined) {
            let linkPrev = document.querySelector(`[data-link="${GlobalPrevChannel}"]`)
            linkPrev.style.fontWeight = 'normal';       
        }
        GlobalPrevChannel = channelNumber;
    }
});