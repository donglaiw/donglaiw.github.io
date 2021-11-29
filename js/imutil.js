function getUrlParam(name){
    var rx = new RegExp('[\&|\?]'+name+'=([^\&\#]+)'),
    val = window.location.search.match(rx);
    return !val ? '':val[1];
}
function getUnique(value, index, self) {
    return self.indexOf(value) === index;
}

// selection color
var color_name_shot=["green","red","white"];
var color_name_seg=["white","red","green"];
function getNextColorId(color, color_name){
    var color_id = color_name.indexOf(color);
    color_id = (color_id + 1) % (color_name.length);
    return color_id;
}
function getNextColor(color, color_name){
    var color_id = color_name.indexOf(color);
    color_id = (color_id + 1) % (color_name.length);
    return color_name[color_id];
}

function getSelection(arr, pref, color_name) {
    for (var i = 0; i < arr.length; ++ i) {
        var bg_color = $(pref+i)[0].style.backgroundColor
        arr[i] = color_name.indexOf(bg_color);
    }
}
// load js file
function loadJs(filename, cb){
    $.get(filename).done(function(){
        $.getScript(filename, cb);
     }).fail(function(){
        alert("can't find file: " + filename)
     });
}
// printf 
function printfd(im_id, num_digit){
    for(var i=1; i<num_digit; i++){
        if(im_id<Math.pow(10,i)){
            im_id = '0'.repeat(num_digit-i)+im_id;
            return im_id;
        }
    }
    return im_id;
}
function isCharNumber(c) {
  return c >= '0' && c <= '9';
}
function getFileName(name_template, im_id){
    var st = name_template.lastIndexOf('%')
    var lt = st
    while(isCharNumber(name_template[lt + 1])){
        lt += 1;
    }
    var to_replace = name_template.substr(st, lt - st + 2)
    var out = im_id; 

    if(name_template[st + 1] == '0'){
        // need to pad 0
        out = printfd(im_id, parseInt(to_replace.substr(2, to_replace.length-3)));
    }
    return name_template.replace(to_replace, out)
}

// arr <-> str
function updateArr(index_old, value_old, index_new, value_default){
    var value_new = '';
    for(var a in index_new){
        var tmp_id = index_old.indexOf(index_new[a])
        if (tmp_id==-1){
            value_new += value_default + ',';
        }else{
            value_new += (value_old[tmp_id] + ',');
         }
    }
    return value_new.substr(0, value_new.length-1);
}
function strToArray(input_str){
    var output_array = input_str.split(",");
    for (a in output_array){
        if (output_array[a].includes('-')){
            var tmp_array = output_array[a].split("-");
            for (b in tmp_array){
                tmp_array[b] = parseInt(tmp_array[b]);
            }
            output_array[a] = range(tmp_array[0], tmp_array[1]+1);
        }else{
            output_array[a] = parseInt(output_array[a]);
        }
    }
    return output_array.flat();
}
function strToArrayRemoveLast(input_str){
    // remove the last ;
    if(input_str[input_str.length-1]==';'){
        input_str = input_str.substr(0,input_str.length-1);
    }
    var output_array = input_str.split(";");
    for (a in output_array){
        output_array[a] = strToArray(output_array[a]);
    }
    return output_array;
}
