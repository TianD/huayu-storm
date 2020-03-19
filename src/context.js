import React from 'react';

export const ModalVisibleContext = React.createContext({
    visible: false,
    changeVisible: (value) => {
        this.visible = value
    },
    project_list: [],
    changeProjectList: (value)=>{
        this.project_list = value
    },
    project: null,
    changeProject: (value)=>{
        this.project = value
    }
});
