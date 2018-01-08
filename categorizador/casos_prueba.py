caso_nivelesCompletos_UnElemento = \
    {
        "categories": [
            {
                "category": "category1",
                "horse_powers": [
                    {
                        "horse_power": "HP1",
                        "serial_ranges": [
                            {
                                "serial_range": "serial1",
                                "components": [
                                    {
                                        "component": "component1",
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
                "horse_powers": [
                    {
                        "horse_power": "HP1 ",
                        "serial_ranges": [
                            {
                                "serial_range": "serial1",
                                "components": [
                                    {
                                        "component": "component1",
                                    },
                                    {
                                        "component": "component2",
                                    },
                                    {
                                        "component": "component3",
                                    },
                                    {
                                        "component": "component4",
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
                "horse_powers": [
                    {
                        "horse_power": "HP1 ",
                        "serial_ranges": [
                            {
                                "serial_range": "serial1",
                                "components": [
                                    {
                                        "component": "component1",
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            {
                "category": "category2",
                "horse_powers": [
                    {
                        "horse_power": "HP2",
                        "serial_ranges": [
                            {
                                "serial_range": "serial2",
                                "components": [
                                    {
                                        "component": "component2",
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            {
                "category": "category3",
                "horse_powers": [
                    {
                        "horse_power": "HP3",
                        "serial_ranges": [
                            {
                                "serial_range": "serial3",
                                "components": [
                                    {
                                        "component": "component3",
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
                "horse_powers": [
                    {
                        "horse_power": "HP1",
                        "serial_ranges": [
                            {
                                "serial_range": "serial1",
                                "components": [
                                    {
                                        "component": "component1",
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            {
                "category": "category2",
                "horse_powers": [
                    {
                        "horse_power": "HP1",
                        "serial_ranges": [
                            {
                                "serial_range": "serial1",
                                "components": [
                                    {
                                        "component": "component1",
                                    },
                                    {
                                        "component": "component2",
                                    },
                                    {
                                        "component": "component3",
                                    }

                                ]
                            },
                            {
                                "serial_range": "serial2",
                                "components": [
                                    {
                                        "component": "component1",
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            {
                "category": "category3",
                "horse_powers": [
                    {
                        "horse_power": "HP1",
                        "serial_ranges": [
                            {
                                "serial_range": "serial1",
                                "components": [
                                    {
                                        "component": "component1",
                                    },
                                    {
                                        "component": "component2",
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
