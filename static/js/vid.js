var vid

function checkConverting() {
    var xhr = new XMLHttpRequest()
    xhr.open('GET', '/checkconverting/' + vid)
    xhr.onload = () => {
        if (xhr.responseText.length) {
            document.getElementById('btn-converting').style['display'] = 'inline-block'
            setTimeout(pendforfile, 5000)
        }
        else {
            checkHasFile()
        }
    }
    xhr.send()
}

function checkHasFile() {
    var xhr = new XMLHttpRequest()
    xhr.open('GET', '/checkfile/' + vid)
    xhr.onload = () => {
        if (xhr.responseText.length) {
            document.getElementById('btn-download').style['display'] = 'inline-block'
        }
        else {
            document.getElementById('btn-convert').style['display'] = 'inline-block'
        }
    }
    xhr.send()
}

function pendforfile() {
    var xhr = new XMLHttpRequest()
    xhr.open('GET', '/checkconverting/' + vid)
    xhr.onload = () => {
        if (xhr.responseText.length) {
            setTimeout(pendforfile, 2500)
        }
        else {
            document.getElementById('btn-converting').style['display'] = 'none'
            document.getElementById('btn-download').style['display'] = 'inline-block'
        }
    }
    xhr.send()
}

window.onload = () => {
    vid = document.getElementById('action-btn').getAttribute('vid')
    checkConverting()
    document.getElementById('btn-convert').addEventListener('click', () => {
        xhr = new XMLHttpRequest()
        xhr.open('GET', '/start/' + vid)
        xhr.onload = () => {
            if (xhr.responseText.length) {
                document.getElementById('btn-convert').style['display'] = 'none'
                document.getElementById('btn-converting').style['display'] = 'inline-block'
                setTimeout(pendforfile, 5000)
            }
        }
        xhr.send()
    })
}