function main() {
    window.addEventListener("load", function() {
        var metaRefresh = document.querySelector("meta[http-equiv='refresh']");
        if (metaRefresh) {
            removeMetaRefresh(metaRefresh);
            if (timeToPayElement())
                setCountDownTimer();
            setPageRefreshTimer();
        }
    });
}

function removeMetaRefresh(metaRefresh) {
    metaRefresh.remove();
    window.stop();
    document.execCommand("Stop"); // IE
}

function setCountDownTimer() {
    var timeToPayInSeconds = parseInt(timeToPayElement().dataset.timeToPay);
    globalPayDeadline = new Date();
    globalPayDeadline.setSeconds(globalPayDeadline.getSeconds() + timeToPayInSeconds);
    setInterval(displayCountDown, 100);
}

function displayCountDown() {
    var now = new Date();
    var timeToPayInMilliseconds = globalPayDeadline - now;
    var timeToPayInSeconds = Math.max(timeToPayInMilliseconds / 1000, 0);
    timeToPayElement().textContent = secondsToTime(timeToPayInSeconds);
    timeToPayBarElement().value = timeToPayInSeconds;
}

function timeToPayElement() {
    return document.getElementById('time-to-pay');
}

function timeToPayBarElement() {
    return document.getElementById('time-to-pay-bar');
}

function secondsToTime(seconds) {
    var date = new Date(0);
    date.setSeconds(seconds);
    var time = date.toISOString().substr(11, 8);
    if (time.startsWith('00:')) time = time.substr(3);
    if (time.startsWith('0')) time = time.substr(1);
    return time;
}

function setPageRefreshTimer() {
    globalStateHash = document.querySelector('body').dataset.stateHash;
    setInterval(refreshPageIfChanged, 1000);
}

function refreshPageIfChanged() {
    var stateHashUrl = window.location.href.replace('/auto', '').replace('/manual', '') + '/state_hash';

    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function() {
        if (xmlhttp.readyState == XMLHttpRequest.DONE) {
           if (xmlhttp.status == 200) {
               var newStateHash = xmlhttp.responseText;
               if (newStateHash !== globalStateHash)
                    window.location.reload();
           }
        }
    };
    xmlhttp.open("GET", stateHashUrl, true);
    xmlhttp.send();
}

main();
