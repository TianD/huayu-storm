import React, { Component } from 'react';
import { Modal, Table, message } from 'antd';
import copy from 'copy-to-clipboard';
import { ModalVisibleContext } from '../context';
import api from '../api'

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
        copy(e['path'])
        message.info("复制到剪贴板.")
    }

    render() {
        return (
            <ModalVisibleContext.Consumer>
                {({ visible, changeVisible }) => (
                    <Modal
                        title={this.props.shot['label']}
                        width={'70%'}
                        height={'80%'}
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
                        <div>
                            <img
                                alt="example"
                                //todo use global url
                                style = {{width: '100%', height: '100%'}}
                                src={api.get_thumbnail_url(this.props.shot)}
                            />
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
                        </div>

                    </Modal>
                )}
            </ModalVisibleContext.Consumer>
        )
    }
}

export default DetailView