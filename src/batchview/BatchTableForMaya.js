import React, { Component } from 'react';
import { Table, Button, Upload, Select, Row, Col } from 'antd';
import { PlayCircleTwoTone, RestTwoTone } from '@ant-design/icons';


//todo , read file from dir
//todo , process maya file , rendering ?
//todo , read maya layers , set to lr(dir)

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
        title: '文件',
        dataIndex: 'filepath',
        key: 'Filepath',
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
                <Button style={{margin: 3}} ghost shape="circle" icon={<PlayCircleTwoTone twoToneColor="#52c41a" />} />
                <Button style={{margin: 3}} ghost shape="circle" icon={<RestTwoTone twoToneColor="#eb2f96" />} />
            </span>
        )
    }
]

class BatchTableForMaya extends Component {
    render() {
        return (
            <div>
                <Row>
                    <Col span={8}>
                        <Select placeholder="选择项目" style={{margin: 12}}></Select>
                        <Upload
                            showUploadList={false}>
                            <Button  style={{margin: 12}}>选择文件</Button>
                        </Upload>
                    </Col>
                    <Col span={8} offset={8}>
                        <Button  style={{margin: 12}}>清空</Button>
                        <Button  style={{margin: 12}}>全部开始</Button>
                    </Col>
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

export default BatchTableForMaya