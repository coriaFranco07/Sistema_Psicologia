

var myChart;
var myChartPagos;
var myChartPend;
var myChartYear;

function gera_cor(qtd=1){
    var bg_color = []
    var border_color = []
    for(let i = 0; i < qtd; i++){
        let r = Math.random() * 255;
        let g = Math.random() * 255;
        let b = Math.random() * 255;
        bg_color.push(`rgba(${r}, ${g}, ${b}, ${0.2})`)
        border_color.push(`rgba(${r}, ${g}, ${b}, ${1})`)
    }
    
    return [bg_color, border_color];
    
}

function renderiza_deuda_total(url){  
    fetch(url, {
        method: 'get',
    }).then(function(result){
        return result.json()
    }).then(function(data){
        document.getElementById('deuda_total').innerHTML = data.total
    })

}

function renderiza_pago_total(url){  
    fetch(url, {
        method: 'get',
    }).then(function(result){
        return result.json()
    }).then(function(data){
        document.getElementById('pago_total').innerHTML = data.total
    })

}


function renderiza_presupuesto(url){  
    fetch(url, {
        method: 'get',
    }).then(function(result){
        return result.json()
    }).then(function(data){
        document.getElementById('presupuesto').innerHTML = data.total
    })

}


function renderiza_reclamos_periodo(url){

    

    fetch(url, {
        method: 'get',
    }).then(function(result){
        
        return result.json()
    }).then(function(data){

        
        
        const ctx = document.getElementById('reclamos_periodos').getContext('2d');
        
        
        
        if (myChart) {
            myChart.destroy();
        }

    
        

        var core_colors_reclamos = gera_cor(qtd=12)

        
        
        myChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Reclamos'],
                datasets: [{
                    
                    data: data.cant,
                    backgroundColor: core_colors_reclamos[0],
                    borderColor: core_colors_reclamos[1],
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true,
                        
                    }
                },
                label: {
                    show: true,
                    position: 'center',
                    
                },
                labelLine: {
                    show: false
                },
                indexAxis: 'y',
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Cantidad de Movimientos - conjunción de filtrado',
                            font: {
                                family: 'Arial',
                                size: 24,
                                weight: 'bold',
                                lineHeight: 1.2,
                              },
                        },
                        ticks: {
                            font: {
                              size: 24,
                            }
                          }
                        
                        
                    },
                    y: {
                        barThickness:{
                            color: 'white',
                            fontSize:30,
                        },
                        title: {
                            display: true,
                            text: 'Movimientos',
                            font: {
                                family: 'Arial',
                                size: 20,
                                weight: 'bold',
                                lineHeight: 1.2,
                              },
                        },
                        ticks: {
                            font: {
                              size: 24,
                            }
                          }
                        
                        
                    }
                },
                barThickness: 20,
                plugins:{
                    
                    tooltip: {
                        titleFont: {
                          size: 20
                        },
                        bodyFont: {
                          size: 16
                        },
                        footerFont: {
                          size: 20 // there is no footer by default
                        }
                      },
                
                    
                },
            },
        });

        
      
      
        
        
    
        
    })


    

}



function renderiza_despesas_mensal(){
    const ctx = document.getElementById('despesas_mensal').getContext('2d');
    var cores_despesas_mensal = gera_cor(qtd=12)
    const myChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'],
            datasets: [{
                label: 'Despesas',
                data: [12, 19, 3, 5, 2, 3, 12, 19, 3, 5, 2, 3],
                backgroundColor: "#CB1EA8",
                borderColor: "#FFFFFF",
                borderWidth: 0.2
            }]
        },
        
    });
}

function renderiza_tipos_reclamos(url){

    fetch(url, {
        method: 'get',
    }).then(function(result){
        return result.json()
    }).then(function(data){
        
        
        const ctx = document.getElementById('tipos_reclamos').getContext('2d');
        var cores_produtos_mais_vendidos = gera_cor(qtd=4)
        const myChart = new Chart(ctx, {
            type: 'pie',
            radius: '5%',
            center: ['50%', '50%'],
            selectedMode: 'single',
            data: {
                labels: data.labels,
                
                datasets: [{
                    label: 'Importe $',
                    data: data.data,
                    backgroundColor: cores_produtos_mais_vendidos[0],
                    borderColor: cores_produtos_mais_vendidos[1],
                    borderWidth: 1,
                    textStyle: {
                        fontSize: '36',
                        
                      },
                },
                /*
                {
                    label: 'Cantidad',
                    data: data.Cant,
                    backgroundColor: cores_produtos_mais_vendidos[0],
                    borderColor: cores_produtos_mais_vendidos[1],
                    borderWidth: 1 
                }
                */
            ]
            },
            options: {
                responsive: true,
                legend: {
                  display: true,
                  position:'bottom',
                  textStyle: {
                    fontSize: '20',
                  },

                },
                
                tooltips: {
                  callbacks: {
                      label: function(tooltipItem, data) {
                      var dataset = data.datasets[tooltipItem.datasetIndex];
                      var index = tooltipItem.index;
                      return dataset.labels[index] + ': ' + dataset.data[index];
                      }
                    },
                    textStyle:{
                        color : '#fff',
                        fontWeight : 'bold',
                        fontFamily : 'sans-serif',
                        fontSize : 18,




                    },

                  
                  
                

                 },

                 plugins:{
                    legend:{

                        title:{
                           // display: true,
                            //text:'Cant. Pend. por Tipo',
                            //font: {
                            //    size: 36
                            //}
                        },
                        labels: {
                            // This more specific font property overrides the global property
                            font: {
                                size: 16
                            }
                        }
                    },
                    tooltip: {
                        titleFont: {
                          size: 20
                        },
                        bodyFont: {
                          size: 16
                        },
                        footerFont: {
                          size: 20 // there is no footer by default
                        }
                      },
                
                    
                },
                 aspectRatio: 1.4,
              }
            
        });


    })
  
}



function renderiza_ejemplo_tipos(url){



    fetch(url, {
        method: 'get',
    }).then(function(result){
        return result.json()
    }).then(function(data){
        
        const ctx = document.getElementById('funcionarios_do_mes').getContext('2d');
        var cores_funcionarios_do_mes = gera_cor(qtd=4)
        const myChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.data,
                    backgroundColor: cores_funcionarios_do_mes[0],
                    borderColor: cores_funcionarios_do_mes[1],
                    borderWidth: 1
                }]
            },
            
        });


    })

}



function renderiza_ejemplo_graficos(url){



    fetch(url, {
        method: 'get',
    }).then(function(result){
        return result.json()
    }).then(function(data){

        const ctx = document.getElementById('lotes_por_periodo').getContext('2d');
        var cores_funcionarios_do_mes = gera_cor(qtd=4)
        const myChart = new Chart(ctx, {
            type: 'polarArea',
            legend: {
                top: '5%',
                left: 'center'
            },
            emphasis: {
                label: {
                  show: true,
                  fontSize: 40,
                  fontWeight: 'bold'
                }
              },
            
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.data,
                    backgroundColor: cores_funcionarios_do_mes[1],
                    borderColor: cores_funcionarios_do_mes[0],
                    borderWidth: 1
                }]
            },
            
        });

        
       


    })

}

function renderiza_reclamosenlotes(url){

    fetch(url, {
        method: 'get',
    }).then(function(result){
        return result.json()
    }).then(function(data){
        
        const ctx = document.getElementById('reclamos_en_lotes').getContext('2d');
        var cores_produtos_mais_vendidos = gera_cor(qtd=4)
        const myChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'reclamos',
                    data: data.data,
                    backgroundColor: cores_produtos_mais_vendidos[0],
                    borderColor: cores_produtos_mais_vendidos[1],
                    borderWidth: 1
                }]
            },
            
        });


    })
  
}

function renderiza_cantportipo(url){



    fetch(url, {
        method: 'get',
    }).then(function(result){
        return result.json()
    }).then(function(data){
        
        const ctx = document.getElementById('cantportipo').getContext('2d');
        
        var cores_funcionarios_do_mes = gera_cor(qtd=4)
       
        const myChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.labels,
                datasets: [{
                    labels: data.label,
                    data: data.data,
                    backgroundColor: cores_funcionarios_do_mes[0],
                    borderColor: cores_funcionarios_do_mes[1],
                    borderWidth: 1
                }]
            },
           
            options: {
                plugins:{
                    legend:{

                        title:{
                           // display: true,
                            //text:'Cant. Pend. por Tipo',
                            //font: {
                            //    size: 36
                            //}
                        },
                        labels: {
                            // This more specific font property overrides the global property
                            font: {
                                size: 16
                            }
                        }
                    },
                    tooltip: {
                        titleFont: {
                          size: 20
                        },
                        bodyFont: {
                          size: 16
                        },
                        footerFont: {
                          size: 20 // there is no footer by default
                        }
                      },
                
                    
                },
                
                aspectRatio: 1.4,
              }
            
        });


    })

}


function renderiza_tipomov(url){



    fetch(url, {
        method: 'get',
    }).then(function(result){
        return result.json()
    }).then(function(data){
        
        const ctx = document.getElementById('tipomov').getContext('2d');
        var cores_funcionarios_do_mes = gera_cor(qtd=4)
        const myChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.labels,
                datasets: [{
                    labels: "Cantidad",
                    data: data.data,
                    backgroundColor: cores_funcionarios_do_mes[0],
                    borderColor: cores_funcionarios_do_mes[1],
                    borderWidth: 1
                }]
            },
            options: {
                title: {
                    text: 'Graph on Cartesian'
                  },
            }
            
        });


    })

}



function renderiza_filtros_mov(url){

    

    fetch(url, {
        method: 'get',
    }).then(function(result){
        
        return result.json()
    }).then(function(data){

        

       
        var select = document.getElementById('estados_select')
         
          data.movs.forEach(element => {
            mOptions = `<option class="opciones" value="${element.id_std_mov}">${element.dsc_std_mov}</option>`
            select.insertAdjacentHTML('beforeend', mOptions);
            })
            
            $(document).ready(function() {
                $('#estados_select').multiselect({
            templates: {
              button: '<button type="button" class="m-4 form-control multiselect dropdown-toggle btn btn-outline-primary" data-bs-toggle="dropdown" aria-expanded="false"><span class="multiselect-selected-text"></span></button>',
            },
            buttonWidth: '100%',
            includeSelectAllOption: true,
            
            
            buttonText: function(options, select) {
                if (options.length === 0) {
                    return 'Selecciones filtros del Gráfico ...';
                }
                else if (options.length > 2) {
                    return 'Seleccionó más de 3 filtros!';
                }
                 else {
                     var labels = [];
                     options.each(function() {
                         if ($(this).attr('label') !== undefined) {
                             labels.push($(this).attr('label'));
                         }
                         else {
                             labels.push($(this).html());
                         }
                     });
                     return labels.join(', ') + '';
                 }
            }



                });
            });
        
      
      
        
        
    })


    

}


function renderiza_reclamos_pendientes(url){

    fetch(url, {
        method: 'get',
    }).then(function(result){
        return result.json()
    }).then(function(data){
       
        
        const ctx = document.getElementById('reclamos_pendientes').getContext('2d');
        var cores_produtos_mais_vendidos = gera_cor(qtd=4)
        const myChart = new Chart(ctx, {
            type: 'pie',
            radius: '5%',
            center: ['50%', '50%'],
            selectedMode: 'single',
            data: {
                labels: data.labels,
                
                datasets: [{
                    label: 'Importe $',
                    data: data.data,
                    backgroundColor: cores_produtos_mais_vendidos[0],
                    borderColor: cores_produtos_mais_vendidos[1],
                    borderWidth: 1,
                    textStyle: {
                        fontSize: '36',
                      },
                },
                /*
                {
                    label: 'Cantidad',
                    data: data.Cant,
                    backgroundColor: cores_produtos_mais_vendidos[0],
                    borderColor: cores_produtos_mais_vendidos[1],
                    borderWidth: 1 
                }
                */
            ]
            },
            options: {
                responsive: true,
                legend: {
                  display: true,
                  position:'bottom',
                  textStyle: {
                    fontSize: '20',
                  },

                },
                
                tooltips: {
                  callbacks: {
                      label: function(tooltipItem, data) {
                      var dataset = data.datasets[tooltipItem.datasetIndex];
                      var index = tooltipItem.index;
                      return dataset.labels[index] + ': ' + dataset.data[index];
                      }
                    },
                    textStyle:{
                        color : '#fff',
                        fontWeight : 'bold',
                        fontFamily : 'sans-serif',
                        fontSize : 18,




                    },

                  
                  
                

                 },
                
                 plugins:{
                    legend:{

                        title:{
                           // display: true,
                            //text:'Cant. Pend. por Tipo',
                            //font: {
                            //    size: 36
                            //}
                        },
                        labels: {
                            // This more specific font property overrides the global property
                            font: {
                                size: 16
                            }
                        }
                    },
                    tooltip: {
                        titleFont: {
                          size: 20
                        },
                        bodyFont: {
                          size: 16
                        },
                        footerFont: {
                          size: 20 // there is no footer by default
                        }
                      },
                
                    
                },
                 aspectRatio: 1.4,
              }
            
        });


    })
  
}

function renderiza_cantportipopen(url){

    const labeltooptip= (tooltipItem)=>{
        return 'items'
    }

    fetch(url, {
        method: 'get',
    }).then(function(result){
        return result.json()
    }).then(function(data){
        
        const ctx = document.getElementById('cantportipopen').getContext('2d');
        
        var cores_funcionarios_do_mes = gera_cor(qtd=4)
       
        const myChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.labels,
               
                datasets: [{
                    labels: data.label,
                    data: data.data,
                    backgroundColor: cores_funcionarios_do_mes[0],
                    borderColor: cores_funcionarios_do_mes[1],
                    borderWidth: 1
                }]
            },
           
            options: {
                
                dataset: {
                    font: {
                        size: 36
                    }
                },
                responsive: true,
                legend: {
                    display: true,
                    labels: {
                        fontColor: 'rgb(255, 99, 132)',
                        fontFamily: 36,
                    }
                },
                plugins:{
                    legend:{

                        title:{
                           // display: true,
                            //text:'Cant. Pend. por Tipo',
                            //font: {
                            //    size: 36
                            //}
                        },
                        labels: {
                            // This more specific font property overrides the global property
                            font: {
                                size: 16
                            }
                        }
                    },
                    tooltip: {
                        titleFont: {
                          size: 20
                        },
                        bodyFont: {
                          size: 16
                        },
                        footerFont: {
                          size: 20 // there is no footer by default
                        }
                      },
                
                    
                },
                
                
                aspectRatio: 1.4,
              },
            
            
        });


    })

}




function renderiza_filtros_pagos(url){

    

    fetch(url, {
        method: 'get',
    }).then(function(result){
        
        return result.json()
    }).then(function(data){

        

       
        var select = document.getElementById('year_select_pagos')
         
          data.labels.forEach(element => {
            
            mOptions = `<option class="opciones" value="${element}">${element}</option>`
            select.insertAdjacentHTML('beforeend', mOptions);
            })
            
            $(document).ready(function() {
                $('#year_select_pagos').multiselect({
            templates: {
              button: '<button type="button" class="m-4 form-control multiselect dropdown-toggle btn btn-outline-primary" data-bs-toggle="dropdown" aria-expanded="false"><span class="multiselect-selected-text"></span></button>',
            },
            buttonWidth: '100%',
            includeSelectAllOption: true,
            
            
            buttonText: function(options, select) {
                if (options.length === 0) {
                    return 'Selecciones filtros del Gráfico ...';
                }
                else if (options.length > 2) {
                    return 'Seleccionó más de 3 filtros!';
                }
                 else {
                     var labels = [];
                     options.each(function() {
                         if ($(this).attr('label') !== undefined) {
                             labels.push($(this).attr('label'));
                         }
                         else {
                             labels.push($(this).html());
                         }
                     });
                     return labels.join(', ') + '';
                 }
            }



                });
            });
        
      
      
        
        
    })


    

}

function renderiza_filtros_pend(url){

    

    fetch(url, {
        method: 'get',
    }).then(function(result){
        
        return result.json()
    }).then(function(data){

        
        
       
        var select = document.getElementById('year_select_pend')
         
          data.movs.forEach(element => {
            mOptions = `<option class="opciones" value="${element.year}">${element.year}</option>`
            select.insertAdjacentHTML('beforeend', mOptions);
            })
            
            $(document).ready(function() {
                $('#year_select_pend').multiselect({
            templates: {
              button: '<button type="button" class="m-4 form-control multiselect dropdown-toggle btn btn-outline-primary" data-bs-toggle="dropdown" aria-expanded="false"><span class="multiselect-selected-text"></span></button>',
            },
            buttonWidth: '100%',
            includeSelectAllOption: true,
            
            
            buttonText: function(options, select) {
                if (options.length === 0) {
                    return 'Selecciones filtros del Gráfico ...';
                }
                else if (options.length > 2) {
                    return 'Seleccionó más de 3 filtros!';
                }
                 else {
                     var labels = [];
                     options.each(function() {
                         if ($(this).attr('label') !== undefined) {
                             labels.push($(this).attr('label'));
                         }
                         else {
                             labels.push($(this).html());
                         }
                     });
                     return labels.join(', ') + '';
                 }
            }



                });
            });
        
      
      
        
        
    })


    

}




function renderiza_pagos(url){

    

    fetch(url, {
        method: 'get',
    }).then(function(result){
        
        return result.json()
    }).then(function(data){

        
        
        const ctx = document.getElementById('reclamos_pagos').getContext('2d');
        
        
        
        if (myChartPagos) {
            myChartPagos.destroy();
        }

    
        

        var core_colors_reclamos = gera_cor(qtd=12)

        
        
        myChartPagos = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [{
                    labels: data.labels,
                    data: data.data,
                    backgroundColor: core_colors_reclamos[0],
                    borderColor: core_colors_reclamos[1],
                    borderWidth: 1
                }]
            },
            
            options: {
                skipNull: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        
                    }
                },
                label: {
                    show: true,
                    position: 'center',
                    
                },
                labelLine: {
                    show: false
                },
                indexAxis: 'y',
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Cantidad de Pagos',
                            font: {
                                family: 'Montserrat-SemiBold',
                                size: 24,
                                weight: 'bold',
                                lineHeight: 1.2,
                              },
                        },
                        ticks: {
                            font: {
                              size: 24,
                            }
                          }
                        
                        
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Años de Pago',
                            font: {
                                family: 'Montserrat-SemiBold',
                                size: 30,
                                weight: 'bold',
                                lineHeight: 1.2,
                              },
                        },
                        ticks: {
                            font: {
                              size: 24,
                            }
                          }
                        
                        
                    }
                },
                barThickness: 30,
                plugins:{
                    
                    tooltip: {
                        titleFont: {
                          size: 20
                        },
                        bodyFont: {
                          size: 16
                        },
                        footerFont: {
                          size: 20 // there is no footer by default
                        }
                      },
                      
                     
                
                    
                },
                
               
            },

        });

        
      
      
        
        
    
        
    })


    

}


function renderiza_pend(url){

    

    fetch(url, {
        method: 'get',
    }).then(function(result){
        
        return result.json()
    }).then(function(data){

        
        
        const ctx = document.getElementById('reclamos_pend').getContext('2d');
        
        
        
        if (myChartPend) {
            myChartPend.destroy();
        }

    
        

        var core_colors_reclamos = gera_cor(qtd=12)

       
        
        myChartPend = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [{
                    labels: data.labels,
                    data: data.data,
                    backgroundColor: core_colors_reclamos[0],
                    borderColor: core_colors_reclamos[1],
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true,
                        
                    }
                },
                label: {
                    show: true,
                    position: 'center',
                    
                },
                labelLine: {
                    show: false
                },
                indexAxis: 'y',
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'ingresos',
                            font: {
                                family: 'Arial',
                                size: 24,
                                weight: 'bold',
                                lineHeight: 1.2,
                              },
                        },
                        ticks: {
                            font: {
                              size: 24,
                            }
                          }
                        
                        
                    },
                    y: {
                        barThickness:{
                            color: 'white',
                            fontSize:30,
                        },
                        title: {
                            display: true,
                            text: 'Años',
                            font: {
                                family: 'Arial',
                                size: 20,
                                weight: 'bold',
                                lineHeight: 1.2,
                              },
                        },
                        ticks: {
                            font: {
                              size: 24,
                            }
                          }
                        
                        
                    }
                },
                barThickness: 20,
                plugins:{
                    
                    tooltip: {
                        titleFont: {
                          size: 20
                        },
                        bodyFont: {
                          size: 16
                        },
                        footerFont: {
                          size: 20 // there is no footer by default
                        }
                      },
                
                    
                },
            },

        });

        
      
      
        
        
    
        
    })


    

    

}



function renderiza_EstadoYearCantView(url){



    fetch(url, {
        method: 'get',
    }).then(function(result){
        return result.json()
    }).then(function(data){
        



        const myChart =echarts.init(document.getElementById('cantestporaño'));
        var app = {};
        var option;




       const posList = [
        'left',
        'right',
        'top',
        'bottom',
        'inside',
        'insideTop',
        'insideLeft',
        'insideRight',
        'insideBottom',
        'insideTopLeft',
        'insideTopRight',
        'insideBottomLeft',
        'insideBottomRight'
        ];
    app.configParameters = {
    rotate: {
        min: -90,
        max: 90
    },
    align: {
        options: {
        left: 'left',
        center: 'center',
        right: 'right'
        }
    },
    verticalAlign: {
        options: {
        top: 'top',
        middle: 'middle',
        bottom: 'bottom'
        }
    },
    position: {
        options: posList.reduce(function (map, pos) {
        map[pos] = pos;
        return map;
        }, {})
    },
    distance: {
        min: 0,
        max: 100
    }
    };
    app.config = {
    rotate: 90,
    align: 'left',
    verticalAlign: 'middle',
    position: 'insideBottom',
    distance: 15,
    onChange: function () {
        const labelOption = {
        rotate: app.config.rotate,
        align: app.config.align,
        verticalAlign: app.config.verticalAlign,
        position: app.config.position,
        distance: app.config.distance
    };
    myChart.setOption({
      series: [
        {
          label: labelOption
        },
        {
          label: labelOption
        },
        {
          label: labelOption
        },
        {
          label: labelOption
        }
      ]
    });
  }
};

const labelOption = {
    show: true,
    position: app.config.position,
    distance: app.config.distance,
    align: app.config.align,
    verticalAlign: app.config.verticalAlign,
    rotate: app.config.rotate,
    formatter: function(params) {
      // Si el valor es 0, muestra "Sin datos"
      if (params.value === 0) {
        return '{a| }';
      }
      // De lo contrario, muestra el valor normal
      return params.seriesName + ' ' + params.value;
    },
    fontSize: 12,
    rich: {
      a: {
        color: '#777' // Color del texto normal
      },
      name: {}
    }
  };
  
option = {
 title:{
    text: 'RECLAMOS'
 },
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'shadow'
    }
  },
  legend: {
    data: data.labels,
    textStyle:{
        color: '#999',
        fontWeight: 'bolder',
    }
  },
  toolbox: {
    show: true,
    orient: 'vertical',
    left: 'right',
    top: 'center',
    feature: {
      mark: { show: true },
      dataView: { show: true, readOnly: false },
      magicType: { show: true, type: ['line', 'bar', 'stack'] },
      restore: { show: true },
      saveAsImage: { show: true, name: 'Reclamos' }
    }
  },
  xAxis: [
    {
        
      type: 'category',
      axisTick: { show: false },
      data: data.data,
      axisLabel:{
        fontWeight :'bolder',
        fontSize: 14,
        color: 'red',

      },
      splitLine: {
        show: true,
        lineStyle: {
                color: 'gray',
                type: 'dotted',
                width: 0.75,
                
        }

      }
      
      
    }
  ],
  yAxis: [
    {
      type: 'value',
      splitLine: {
        lineStyle: {
            color: 'blue',
            with: 1,
        }
    }

    },
    
  ],
  series: data.cant.map((d) => {
    return {
      name: d.name,
      type:'bar',
      barGap:0,
      label: labelOption,
      emphasis: {
        focus: 'series'
      },
      data: d.data,
    }
  }),
};

option && myChart.setOption(option);

        
    });
          

       


}