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

caso_variosProductos = \
    {
        "products": [
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
            },
            {
                "part_number": "2189-832498A 1",
                "manufacturer": "Mercury Quicksilver",
                "diagram_number": "#2",
                "product": "2189-832498A 1 - TOP COWL ASSEMBLY O",
            }
        ]
    }

