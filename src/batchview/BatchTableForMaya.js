import React, {Component} from 'react';
import {Table} from 'antd';

const dataSource = [
    {
        key: '1',
        id: 1,
        status: '就绪',
        shot: 'xx.ma',
        thumbnail: "https://gw.alipayobjects.com/zos/rmsportal/JiqGstEfoWAOHiTxclqi.png",
        taskType: 'Nuke模板',
    },
    {
        key: '2',
        id: 2,
        status: '就绪',
        shot: 'xx.ma',
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
        render: (text) => <image src={text}/>
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
              <a>Start {record.name}</a>
              <a>Delete</a>
            </span>
        )
    }
]

class BatchTableForMaya extends Component {
    render() {
        return (
            <Table
                dataSource={dataSource}
                columns={columns}/>
        )
    }
}

export default BatchTableForMaya