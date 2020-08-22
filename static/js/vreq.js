(function () {
    const vid = $('#action-btn').attr('vid')
    const ext = $('#action-btn').attr('ext')

    function showButton(btn) {
        $('#btn-convert').css('display', 'none')
        $('#btn-converting').css('display', 'none')
        $('#btn-download').css('display', 'none')
        $('#btn-' + btn).css('display', 'inline-block')
    }

    function checkConvert() {
        $.post('/post', {
            action: 'convert', vid: vid, ext: ext
        }, function (res) {
            if (res.length) {
                checkHasFile()
            }
            else {
                showButton('download')
                setTimeout(checkComplete, 5000)
            }
        })
    }

    function checkHasFile() {
        $.post('/post', {
            action: 'file', vid: vid, ext: ext
        }, function (res) {
            if (res.length) {
                showButton('convert')
            }
            else {
                showButton('download')
            }
        })
    }

    function checkComplete() {
        $.post('/post', {
            action: 'complete', vid: vid, ext: ext
        }, function (res) {
            if (res.length) {
                switch (res) {
                    case 'complete':
                        showButton('download')
                        break;
                    case 'error':
                        alert('An error occurred on server side. Please try again later, or contact the service provider.')
                        window.location.replace('/')
                        break;
                }
            }
            else {
                setTimeout(checkComplete, 2500)
            }
        })
    }

    $('#btn-convert').click(function (evt) {
        $.post('/post', {
            action: 'start', vid: vid, ext: ext
        }, function (res) {
            if (res.length) {
                showButton('download')
            }
            else {
                showButton('converting')
                setTimeout(checkComplete, 5000)
            }
        })
    })
    checkConvert()
})()