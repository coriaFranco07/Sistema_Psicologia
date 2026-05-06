function modal_data(url){
    $.ajax({
        url: url,
        cache: false
      })
      .done(function( html ) {
       
        $('#data').load(url, function(){
        
            $(this).modal('show')
        })
      })
      .fail(function( jqXHR, textStatus, error ) {
        
        window.location.reload();

      });

      

}

function modal_cerrar(){
    $('#data').modal('hide')

}

function registrar(){
     
     $.ajax({
        data: $('#form_add').serialize(),
        url: $('#form_add').attr('action'),
        type:$('#form_add').attr('method'),
        success: function(response){
            
            activar_boton()
            
            notificacionSuccess(response.mensaje)
        },
        error: function(error){
            notificacionError(error.responseJSON.mensaje)
            mostrarErrores(error)
            $('#btn_add').prop('disabled',false);

        }
    }) 
}

function activar_boton(){
    if($('#btn_add').prop('disabled')){
        $('#btn_add').prop('disabled',false);
    }else{
        $('#btn_add').prop('disabled',true);
    }
}

function mostrarErrores(errores){
    $('#errores').html("");
    let error =""
    for (let item in errores.responseJSON.error){
        error += '<div class="alert alert-danger h-50" <strong>' + errores.responseJSON.error[item] + '</strong></div>'
        
    }
    $('#errores').append(error);
    
    
    
}

function notificacionError(mensaje){
    Swal.fire({
        title: 'Error',
        text: mensaje,
        icon: 'error'
    })
}

function notificacionSuccess(mensaje){
    console.log('000000000000000000')
    console.log(mensaje)
    Swal.fire({
        title: 'Registrado',
        text: mensaje,
        icon: 'success',
        confirmButtonText: "Aceptar",
        
    }).then(resultado => {
        if (resultado.value) {
            console.log('000000000000000000')
            window.location.reload();
        }
    })
}
function registrar_img(slug){
            
            var data = new FormData($('#form_add').get(0));
            data.append('slug', slug);
            
            $.ajax({
                url: $('#form_add').attr('action'),
                type:$('#form_add').attr('method'),
                data: data,
                contentType: 'multipart/form-data',
                processData: false,
                contentType: false,
                success: function(response) {
                    notificacionSuccess(response.mensaje)
                },
                error: function(error){
                    notificacionError(error.responseJSON.mensaje)
                    mostrarErrores(error)
                    $('#btn_add').prop('disabled',false);
        
                }
            });
            return false;
               
             
}


function registrar2(){
    
    var pathname = window.location.pathname;
alert(pathname);
}

function eliminar_img(slug){
   
            console.log()        
    $.ajax({
        data: $('#form_add').serialize(),
        url: $('#form_add').attr('action'),
        type:$('#form_add').attr('method') ,
        dataType: 'json'})
        .done(function( html ) {
            console.log('********///*********')
            console.log(html.responseJSON)   
            notificacionSuccess(html.responseJSON)
        })
        .fail(function( jqXHR, textStatus, error ) {
            console.log('********///*********')
            window.location.reload();
  
        });
  
       
        console.log('********///*********')
}