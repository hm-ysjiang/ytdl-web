(function () {
    var vid
    var ext

    function checkConverting() {
        $.post('/checkconverting', {
            vid: vid, ext: ext
        }, function (res) {
            if (res.length) {
                $('#btn-download').css('display', 'inline-block')
                setTimeout(pendforfile, 5000)
            }
            else {
                checkHasFile()
            }
        })
    }

    function checkHasFile() {
        $.post('/checkfile', {
            vid: vid, ext: ext
        }, function (res) {
            if (res.length) {
                $('#btn-download').css('display', 'inline-block')
            }
            else {
                $('#btn-convert').css('display', 'inline-block')
            }
        })
    }

    function pendforfile() {
        $.post('/checkconverting', {
            vid: vid, ext: ext
        }, function (res) {
            if (res.length) {
                setTimeout(pendforfile, 2500)
            }
            else {
                $('#btn-converting').css('display', 'none')
                $('#btn-download').css('display', 'inline-block')
            }
        })
    }

    vid = $('#action-btn').attr('vid')
    ext = $('#action-btn').attr('ext')
    $('#btn-convert').click(function (evt) {
        $.post('/start', {
            vid: vid, ext: ext
        }, function (res) {
            if (res.length) {
                $('#btn-convert').css('display', 'none')
                $('#btn-converting').css('display', 'inline-block')
                setTimeout(pendforfile, 5000)
            }
        })
    })
    checkConverting()
})()