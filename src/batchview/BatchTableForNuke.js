import React, { Component } from 'react';
import { connect } from 'react-redux';
import { Table, Row, Col, Radio, Cascader, Button } from 'antd';
import { PlayCircleTwoTone, RestTwoTone } from '@ant-design/icons';


function mapStateToProps(state) {
    return {
        project_list: state.project_list,
        get_project_list_failed: state.get_project_list_failed,
        get_project_list_loading: state.get_project_list_loading
    }
}


const dataSource = [
    {
        key: '1',
        id: 1,
        status: '就绪',
        shot: 'EP509_s001_cp_001.nk',
        thumbnail: "https://gw.alipayobjects.com/zos/rmsportal/JiqGstEfoWAOHiTxclqi.png",
        taskType: 'Nuke模板',
    },
    {
        key: '2',
        id: 2,
        status: '就绪',
        shot: 'EP509_s002_cp_001.nk',
        thumbnail: "https://gw.alipayobjects.com/zos/rmsportal/JiqGstEfoWAOHiTxclqi.png",
        taskType: 'Nuke模板',
    },
]

const columns = [
    {
        title: 'Id',
        dataIndex: 'id',
        key: 'id',
    },
    {
        title: '状态',
        dataIndex: 'status',
        key: 'status',
    },
    {
        title: '预览',
        dataIndex: 'thumbnail',
        key: 'thumbnail',
        render: (text) => <image src={text} />
    },
    {
        title: '镜头',
        dataIndex: 'shot',
        key: 'shot'
    },
    {
        title: '任务类型',
        dataIndex: 'taskType',
        key: 'taskType'
    },
    {
        title: 'Action',
        dataIndex: 'action',
        key: 'action',
        render: (text, record) => (
            <span>
                <Button style={{ margin: 3 }} ghost shape="circle" icon={<PlayCircleTwoTone twoToneColor="#52c41a" />} />
                <Button style={{ margin: 3 }} ghost shape="circle" icon={<RestTwoTone twoToneColor="#eb2f96" />} />
            </span>
        )
    }
]

class BatchTableForNuke extends Component {
    render() {
        return (
            <div>
                <Row>
                    <Col span={8}>
                        <Cascader
                            placeholder="选择项目"
                            options={this.props.project_list}
                            style={{ margin: 12 }} />
                    </Col>
                    <Col span={8}>
                        <Radio.Group value={1}>
                            <Radio value={1} style={{ margin: 12 }}>生成Nuke工程</Radio>
                            <Radio value={2} style={{ margin: 12 }}>提交渲染</Radio>
                        </Radio.Group>

                    </Col>
                    <Col span={8}><Button style={{ margin: 12 }}>全部开始</Button></Col>
                </Row>
                <Table
                    tableLayout={"fixed"}
                    dataSource={dataSource}
                    columns={columns}
                    pagination={false}
                />
            </div>
        )
    }
}

export default connect(mapStateToProps)(BatchTableForNuke)