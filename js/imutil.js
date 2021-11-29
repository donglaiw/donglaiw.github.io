function getUrlParam(name){
    var rx = new RegExp('[\&|\?]'+name+'=([^\&\#]+)'),
    val = window.location.search.match(rx);
    return !val ? '':val[1];
}
function getUnique(value, index, self) {
    return self.indexOf(value) === index;
}

function printfd(im_id, num_digit){
    for(var i=1; i<num_digit; i++){
        if(im_id<Math.pow(10,i)){
            im_id = '0'.repeat(num_digit-i)+im_id;
            return im_id;
        }
    }
    return im_id;
}
