import React, {Component} from 'react';
import {Modal} from 'antd';
import {ModalVisibleContext} from './context';

class DetailView extends Component {

    handleOk(e) {
        this.setState({
            visible: false,
        });
    };

    handleCancel(e) {
        this.setState({
            visible: false,
        });
    };

    render() {
        return (
            <ModalVisibleContext.Consumer>
                {(visible, changeVisible) => (
                    <Modal
                        title="Basic Modal"
                        visible={visible}
                        onOk={() => (changeVisible(false))}
                    >
                        <p>Some contents...</p>
                        <p>Some contents...</p>
                        <p>Some contents...</p>
                    </Modal>
                )}
            </ModalVisibleContext.Consumer>
        )
    }
}

export default DetailView