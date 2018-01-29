caso_nivelesCompletos_UnElemento = \
    {
        "categories": [
            {
                "category": "category1",
                "sub_category": [
                    {
                        "category": "HP1",
                        "sub_category": [
                            {
                                "category": "serial1",
                                "sub_category": [
                                    {
                                        "category": "component1",
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    }
casoR_nivelesCompletos_UnElemento = \
    [['',"category1", "HP1", "serial1", "component1"]]

########################################################################################################################
caso_nivelesCompletos_variosElemComponentes = \
    {
        "categories": [
            {
                "category": "category1",
                "sub_category": [
                    {
                        "category": "HP1 ",
                        "sub_category": [
                            {
                                "category": "serial1",
                                "sub_category": [
                                    {
                                        "category": "component1",
                                    },
                                    {
                                        "category": "component2",
                                    },
                                    {
                                        "category": "component3",
                                    },
                                    {
                                        "category": "component4",
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    }

casoR_nivelesCompletos_variosElementosCom = \
    [
        ['',"category1", "HP1", "serial1", "component1"]
        ,['',"category1", "HP1", "serial1", "component2"]
        ,['',"category1", "HP1", "serial1", "component3"]
        ,['',"category1", "HP1", "serial1", "component4"]
    ]
########################################################################################################################
caso_nivelesCompletos_variasCateg_UnElemComp = \
    {
        "categories": [
            {
                "category": "category1",
                "sub_category": [
                    {
                        "category": "HP1 ",
                        "sub_category": [
                            {
                                "category": "serial1",
                                "sub_category": [
                                    {
                                        "category": "component1",
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            {
                "category": "category2",
                "sub_category": [
                    {
                        "category": "HP2",
                        "sub_category": [
                            {
                                "category": "serial2",
                                "sub_category": [
                                    {
                                        "category": "component2",
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            {
                "category": "category3",
                "sub_category": [
                    {
                        "category": "HP3",
                        "sub_category": [
                            {
                                "category": "serial3",
                                "sub_category": [
                                    {
                                        "category": "component3",
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    }

casoR_nivelesCompletos_variasCateg_UnElemComp = \
    [
        ['',"category1", "HP1", "serial1", "component1"]
        ,['',"category2", "HP2", "serial2", "component2"]
        ,['',"category3", "HP3", "serial3", "component3"]
    ]

########################################################################################################################
caso_nivelesCompletos_variasCateg_variasSerial_variosComp = \
    {
        "categories": [
            {
                "category": "category1",
                "sub_category": [
                    {
                        "category": "HP1",
                        "sub_category": [
                            {
                                "category": "serial1",
                                "sub_category": [
                                    {
                                        "category": "component1",
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            {
                "category": "category2",
                "sub_category": [
                    {
                        "category": "HP1",
                        "sub_category": [
                            {
                                "category": "serial1",
                                "sub_category": [
                                    {
                                        "category": "component1",
                                    },
                                    {
                                        "category": "component2",
                                    },
                                    {
                                        "category": "component3",
                                    }

                                ]
                            },
                            {
                                "category": "serial2",
                                "sub_category": [
                                    {
                                        "category": "component1",
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            {
                "category": "category3",
                "sub_category": [
                    {
                        "category": "HP1",
                        "sub_category": [
                            {
                                "category": "serial1",
                                "sub_category": [
                                    {
                                        "category": "component1",
                                    },
                                    {
                                        "category": "component2",
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    }

casoR_nivelesCompletos_variasCateg_variasSerial_variosComp = \
    [
        ['',"category1", "HP1", "serial1", "component1"]
        , ['',"category2", "HP1", "serial1", "component1"]
        , ['',"category2", "HP1", "serial1", "component2"]
        , ['',"category2", "HP1", "serial1", "component3"]
        , ['',"category2", "HP1", "serial2", "component1"]
        , ['',"category3", "HP1", "serial1", "component1"]
        , ['',"category3", "HP1", "serial1", "component2"]
    ]
########################################################################################################################
########################################################################################################################


caso_unProductoRecomendNulo = \
    {
        "part_number": "2189-832500A 1",
        "manufacturer": "Mercury Quicksilver",
        "diagram_number": "#1",
        "product": "2189-832500A 1 - TOP COWL ASSEMBLY O",
        "recomended": None
    }

caso_unProductoRecomendString = \
    {
        "part_number": "2189-832500A 1",
        "manufacturer": "Mercury Quicksilver",
        "diagram_number": "#1",
        "product": "2189-832500A 1 - TOP COWL ASSEMBLY O",
        "recomended": "/newparts/part_search.php?part_num=0355633",
    }

caso_unProductosConRecomendadoUnNivel = \
    {
        "part_number": "2189-832500A 1",
        "manufacturer": "Mercury Quicksilver",
        "diagram_number": "#1",
        "product": "2189-832500A 1 - TOP COWL ASSEMBLY O",
        "recomended": {
            "part_number": "2189-832500A 2",
            "manufacturer": "Mercury Quicksilver",
            "diagram_number": "#1",
            "product": "2189-832500A 2 - TOP COWL ASSEMBLY O",
            "recomended": None
        }
    }


caso_unProductoConRecomVariosNiveles = \
    {
        "product_image": "img/marine_engine/j&e/0334435.jpg",
        "manufacturer": "Evinrude Johnson OMC",
        "product_url": "/newparts/part_details.php?pnum=OMC0334435&pass_title=0334435+%3A+Replaced+by+0355633",
        "diagram_number": "0 ",
        "product": "0334435",
        "recomended": {
            "product_image": None,
            "manufacturer": "Evinrude Johnson OMC",
            "product_url": "/newparts/part_details.php?pnum=OMC0355633&pass_title=0355633+%3A",
            "diagram_number": "0 ",
            "product": "0355633 - DECAL OWNER ATTN",
            "recomended": {
                "part_number": "2189-832500A 2",
                "manufacturer": "Mercury Quicksilver",
                "diagram_number": "#1",
                "product": "2189-832500A 2 - TOP COWL ASSEMBLY O",
                "recomended": {
                    "part_number": "2189-832498A 1",
                    "manufacturer": "Mercury Quicksilver",
                    "diagram_number": "#2",
                    "product": "2189-832498A 1 - TOP COWL ASSEMBLY O",
                    "recomended": "/newparts/part_search.php?part_num=0355633"
                },
                "part_number": "0355633"
            },
            "part_number": "0355633"
        },
        "part_number": "0334435"
    }

caso_ProductosRepetidoConRecomendadoRepetidoUnNivel = \
    {
        "products": [
            {
                "your_price": "$3.09",
                "product_image": "img/marine_engine/j&e/0346151.jpg",
                "manufacturer": "Evinrude Johnson OMC",
                "product_url": "/newparts/part_details.php?pnum=OMC0346151",
                "diagram_number": "3 ",
                "product": "0346151 - Clamp",
                "list_price": "$3.09",
                "recomended": {
                    "your_price": "$12.81",
                    "product_image": None,
                    "manufacturer": "Sierra Marine",
                    "product_url": "/newparts/part_details.php?pnum=SIE18-9135-9",
                    "diagram_number": "3 ",
                    "product": "18-9135-9 - 10-Pack Oetiker Clamp 13/16",
                    "list_price": "<span class=\"strike\">$18.24</span>",
                    "recomended": None,
                    "part_number": "18-9135-9"
                },
                "part_number": "0346151"
            },
            {
                "your_price": "$12.81",
                "product_image": None,
                "manufacturer": "Sierra Marine",
                "product_url": "/newparts/part_details.php?pnum=SIE18-9135-9",
                "diagram_number": "3 ",
                "product": "18-9135-9 - 10-Pack Oetiker Clamp 13/16",
                "list_price": "<span class=\"strike\">$18.24</span>",
                "recomended": None,
                "part_number": "18-9135-9"
            },
        ]
    }


caso_ProductosRepetidoConRecomendadosAnidadosRepetidos = \
    {
        "products": [
            {
                "your_price": "$249.98",
                "product_image": "img/marine_engine/j&e/0586890.jpg",
                "manufacturer": "Evinrude Johnson OMC",
                "product_url": "/newparts/part_details.php?pnum=OMC0586890",
                "diagram_number": "1 ",
                "product": "0586890 - Starter Motor",
                "list_price": "<span class=\"strike\">$251.49</span>",
                "recomended": {
                    "your_price": "$223.64",
                    "product_image": "img/marine_engine/j&e/18-5619.jpg",
                    "manufacturer": "Sierra Marine",
                    "product_url": "/newparts/part_details.php?pnum=SIE18-5619",
                    "diagram_number": "1 ",
                    "product": "18-5619 - Starter, 584799",
                    "list_price": "<span class=\"strike\">$224.99</span>",
                    "recomended": {
                        "your_price": "$194.17",
                        "product_image": "img/marine_engine/j&e/5387.jpg",
                        "manufacturer": "Arco Marine",
                        "product_url": "/newparts/part_details.php?pnum=ARC5387",
                        "diagram_number": "1 ",
                        "product": "5387 - Outboard Starter",
                        "list_price": "<span class=\"strike\">$221.95</span>",
                        "recomended": None,
                        "part_number": "5387"
                    },
                    "part_number": "18-5619"
                },
                "part_number": "0586890"
            },
            {
                "your_price": "$223.64",
                "product_image": "img/marine_engine/j&e/18-5619.jpg",
                "manufacturer": "Sierra Marine",
                "product_url": "/newparts/part_details.php?pnum=SIE18-5619",
                "diagram_number": "1 ",
                "product": "18-5619 - Starter, 584799",
                "list_price": "<span class=\"strike\">$224.99</span>",
                "recomended": {
                    "your_price": "$194.17",
                    "product_image": "img/marine_engine/j&e/5387.jpg",
                    "manufacturer": "Arco Marine",
                    "product_url": "/newparts/part_details.php?pnum=ARC5387",
                    "diagram_number": "1 ",
                    "product": "5387 - Outboard Starter",
                    "list_price": "<span class=\"strike\">$221.95</span>",
                    "recomended": None,
                    "part_number": "5387"
                },
                "part_number": "18-5619"
            },
            {
                "your_price": "$194.17",
                "product_image": "img/marine_engine/j&e/5387.jpg",
                "manufacturer": "Arco Marine",
                "product_url": "/newparts/part_details.php?pnum=ARC5387",
                "diagram_number": "1 ",
                "product": "5387 - Outboard Starter",
                "list_price": "<span class=\"strike\">$221.95</span>",
                "recomended": None,
                "part_number": "5387"
            },
        ]
    }


caso_variosProductosDosConRecomendadosAnidados = \
    {
        "products": [
            {
                "your_price": "$249.98",
                "product_image": "img/marine_engine/j&e/0586890.jpg",
                "manufacturer": "Evinrude Johnson OMC",
                "product_url": "/newparts/part_details.php?pnum=OMC0586890",
                "diagram_number": "1 ",
                "product": "0586890 - Starter Motor",
                "list_price": "<span class=\"strike\">$251.49</span>",
                "recomended": {
                    "your_price": "$223.64",
                    "product_image": "img/marine_engine/j&e/18-5619.jpg",
                    "manufacturer": "Sierra Marine",
                    "product_url": "/newparts/part_details.php?pnum=SIE18-5619",
                    "diagram_number": "1 ",
                    "product": "18-5619 - Starter, 584799",
                    "list_price": "<span class=\"strike\">$224.99</span>",
                    "recomended": {
                        "your_price": "$194.17",
                        "product_image": "img/marine_engine/j&e/5387.jpg",
                        "manufacturer": "Arco Marine",
                        "product_url": "/newparts/part_details.php?pnum=ARC5387",
                        "diagram_number": "1 ",
                        "product": "5387 - Outboard Starter",
                        "list_price": "<span class=\"strike\">$221.95</span>",
                        "recomended": None,
                        "part_number": "5387"
                    },
                    "part_number": "18-5619"
                },
                "part_number": "0586890"
            },
            {
                "your_price": "$223.64",
                "product_image": "img/marine_engine/j&e/18-5619.jpg",
                "manufacturer": "Sierra Marine",
                "product_url": "/newparts/part_details.php?pnum=SIE18-5619",
                "diagram_number": "1 ",
                "product": "18-5619 - Starter, 584799",
                "list_price": "<span class=\"strike\">$224.99</span>",
                "recomended": {
                    "your_price": "$194.17",
                    "product_image": "img/marine_engine/j&e/5387.jpg",
                    "manufacturer": "Arco Marine",
                    "product_url": "/newparts/part_details.php?pnum=ARC5387",
                    "diagram_number": "1 ",
                    "product": "5387 - Outboard Starter",
                    "list_price": "<span class=\"strike\">$221.95</span>",
                    "recomended": None,
                    "part_number": "5387"
                },
                "part_number": "18-5619"
            },
            {
                "your_price": "$194.17",
                "product_image": "img/marine_engine/j&e/5387.jpg",
                "manufacturer": "Arco Marine",
                "product_url": "/newparts/part_details.php?pnum=ARC5387",
                "diagram_number": "1 ",
                "product": "5387 - Outboard Starter",
                "list_price": "<span class=\"strike\">$221.95</span>",
                "recomended": None,
                "part_number": "5387"
            },
            {
                "part_number": "2189-832500A 1",
                "manufacturer": "Mercury Quicksilver",
                "diagram_number": "#1",
                "product": "2189-832500A 1 - TOP COWL ASSEMBLY O",
            },
            {
                "part_number": "2189-832500A 2",
                "manufacturer": "Mercury Quicksilver",
                "diagram_number": "#1",
                "product": "2189-832500A 2 - TOP COWL ASSEMBLY O",
                "recomended": None,
            },
            {
                "part_number": "2189-832498A 1",
                "manufacturer": "Mercury Quicksilver",
                "diagram_number": "#2",
                "product": "2189-832498A 1 - TOP COWL ASSEMBLY O",
                "recomended": None,
            }
        ]
    }

