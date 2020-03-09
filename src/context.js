import React from 'react';

export const ModalVisibleContext = React.createContext({
    visible: false,
    changeVisible: (value) => {
        this.visible = value
    }
});
