import React, {Component} from 'react';
import {Card, Button, Row, Col} from 'antd';

const {Meta} = Card;

class MyCard extends Component {

    componentDidMount() {

    }

    render() {
        return (
            <Card
                hoverable
                style={{width: 320, margin: (10, 10, 10, 10)}}
                type={"inner"}
                cover={<img alt="example" src="https://gw.alipayobjects.com/zos/rmsportal/JiqGstEfoWAOHiTxclqi.png"/>}
                onClick={(event) => this.props.onClick(event)}
            >
                <Row>
                    <Col span={8}><Button type={"link"}>{this.props.shot["label"]}</Button></Col>
                    {/* <Col span={8} offset={8}><Button type={"link"}>Tree01</Button></Col> */}
                </Row>
            </Card>
        )
    }
}

export default MyCard