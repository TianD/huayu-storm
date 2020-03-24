import React, { Component } from 'react';
import { Modal, Table, message } from 'antd';
import copy from 'copy-to-clipboard';
import { ModalVisibleContext } from '../context';
import api from '../api'

const columns = [
    {
        key: 'type',
        title: '类型',
        dataIndex: 'type'
    },
    {
        key: 'path',
        title: '文件',
        dataIndex: 'path'
    }
]

class DetailView extends Component {
    state = {
        visible: false,
        dataSource: [],
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

    componentWillReceiveProps(nextProps) {
        if (JSON.stringify(this.props) !== JSON.stringify(nextProps)){
            api.get_detail(nextProps.shot, (response)=>{
                this.setState({
                    dataSource: response.data
                })
            })
        }
    }

    render() {
        let {dataSource} = this.state
        return (
            <ModalVisibleContext.Consumer>
                {({ visible, changeVisible }) => (
                    <Modal
                        title={this.props.shot['label']}
                        width={960}
                        height={'50%'}
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
                                dataSource={dataSource}
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