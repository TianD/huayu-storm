import React, { Component } from 'react';
import { Modal, Table, message } from 'antd';
import copy from 'copy-to-clipboard';
import { ModalVisibleContext } from '../context';

const columns = [
    {
        key: 'Type',
        title: 'type',
        dataIndex: 'type'
    },
    {
        key: 'Path',
        title: 'path',
        dataIndex: 'path'
    }
]

const data = [
    {
        type: 'maya',
        path: 'd:/abc.ma'
    }
]

class DetailView extends Component {
    state = {
        visible: false,
        selectedRowKeys: [],
    };

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

    copy2clipboard(e) {
        copy('abc')
        message.info("复制到剪贴板.")
    }

    render() {
        let { selectedRowKeys } = this.state
        let rowSelection = {
            selectedRowKeys,
            onChange: this.copy2clipboard,
        };
        return (
            <ModalVisibleContext.Consumer>
                {({ visible, changeVisible }) => (
                    <Modal
                        title="Basic Modal"
                        visible={visible}
                        closable={false}
                        centered={true}
                        onOk={
                            () => {
                                changeVisible(false)
                            }
                        }
                        onCancel={
                            () => {
                                changeVisible(false)
                            }
                        }
                    >
                        <Table
                            columns={columns}
                            dataSource={data}
                            pagination={false}
                            onRow={record => {
                                return {
                                    onClick: (e) => { this.copy2clipboard(record) }, // 点击行
                                }
                            }
                            }
                        />
                    </Modal>
                )}
            </ModalVisibleContext.Consumer>
        )
    }
}

export default DetailView