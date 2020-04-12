import React, { Component } from 'react';
import { Modal, Table, message } from 'antd';
import copy from 'copy-to-clipboard';
import api from '../api'

const columns = [
    {
        key: 'type',
        title: '类型',
        dataIndex: 'type',
        render: (value, row, index) => {
            const obj = {
                children: value,
                props: {}
            };
            if (row['index'] === 0) {
                obj.props.rowSpan = row['rowSpan'];
            } else {
                obj.props.rowSpan = 0
            }
            return obj;
        }
    },
    {
        key: 'path',
        title: '文件',
        dataIndex: 'path'
    }
]

class DetailView extends Component {
    state = {
        dataSource: [],
    };

    handleOk(e) {
        this.props.changeVisible(false);
    };

    handleCancel(e) {
        this.props.changeVisible(false);
    };

    copy2clipboard(e) {
        copy(e['dir'])
        message.info("复制到剪贴板.")
    }

    componentWillReceiveProps(nextProps) {
        if (JSON.stringify(this.props) !== JSON.stringify(nextProps)) {
            api.get_detail(nextProps.shot).then((response) => {
                this.setState({
                    dataSource: response.data
                })
            })
        }
    }

    render() {
        let { dataSource } = this.state
        return (
            <Modal
                title={this.props.shot['label']}
                width={800}
                height={'70%'}
                visible={this.props.visible}
                closable={false}
                centered={true}
                onOk={
                    () => {
                        this.props.changeVisible(false)
                    }
                }
                onCancel={
                    () => {
                        this.props.changeVisible(false)
                    }
                }
            >
                <div>
                    <div
                        style={{ textAlign: "center" }}
                    >
                        <img
                            style={{ width: "auto", maxHeight: 360, height: "auto", maxWidth: 700 }}
                            alt="example"
                            src={api.get_thumbnail_url(this.props.shot)}
                        />
                    </div>

                    <Table
                        columns={columns}
                        dataSource={dataSource}
                        pagination={false}
                        onRow={record => {
                            return {
                                onClick: (e) => {
                                    this.copy2clipboard(record)
                                }, // 点击行
                            }
                        }
                        }
                    />
                </div>
            </Modal>
        )
    }
}

export default DetailView