import './styles.scss';

import React, { useCallback, useEffect, useState } from 'react';
import { useParams } from 'react-router';
import { Bar } from 'react-chartjs-2';
import 'chart.js/auto';
import { Row, Col } from 'antd/lib/grid';
import Button from 'antd/lib/button';
import Empty from 'antd/lib/empty';
import Radio from 'antd/lib/radio';
import Result from 'antd/lib/result';
import Text from 'antd/lib/typography/Text';
import Title from 'antd/lib/typography/Title';

import { getCore } from 'cvat-core-wrapper';
import GoBackButton from 'components/common/go-back-button';
import CVATLoadingSpinner from 'components/common/loading-spinner';

const core = getCore();

const BAR_HEIGHT_PX = 22;
const TYPE_COLORS = ['#1890ff', '#fa8c16', '#52c41a', '#eb2f96', '#722ed1', '#13c2c2', '#faad14', '#8c8c8c'];

interface LabelCount {
    id: number;
    name: string;
    count: number;
    by_type: Record<string, number>;
}

interface AnnotationCounts {
    task_id: number;
    total: number;
    types: string[];
    labels: LabelCount[];
}

type Grouping = 'total' | 'type';

type PageState =
    | { status: 'loading' }
    | { status: 'failed'; message: string }
    | { status: 'loaded'; data: AnnotationCounts };

interface ChartProps {
    labels: LabelCount[];
    types: string[];
    grouping: Grouping;
}

function AnnotationCountsChart({ labels, types, grouping }: ChartProps): JSX.Element {
    const datasets = grouping === 'total' ? [{
        label: 'Annotations',
        data: labels.map((label) => label.count),
        backgroundColor: TYPE_COLORS[0],
    }] : types.map((type, index) => ({
        label: type,
        data: labels.map((label) => label.by_type[type] ?? 0),
        backgroundColor: TYPE_COLORS[index % TYPE_COLORS.length],
    }));

    return (
        <div className='cvat-annotation-counts-chart' style={{ height: labels.length * BAR_HEIGHT_PX + 60 }}>
            <Bar
                data={{ labels: labels.map((label) => label.name), datasets }}
                options={{
                    indexAxis: 'y',
                    maintainAspectRatio: false,
                    plugins: { legend: { display: grouping === 'type' } },
                    scales: {
                        x: { stacked: true },
                        y: { stacked: true, ticks: { autoSkip: false } },
                    },
                }}
            />
        </div>
    );
}

function AnnotationCountsPage(): JSX.Element {
    const { tid } = useParams<{ tid: string }>();
    const [state, setState] = useState<PageState>({ status: 'loading' });
    const [grouping, setGrouping] = useState<Grouping>('total');

    const load = useCallback(async (): Promise<void> => {
        setState({ status: 'loading' });
        try {
            const response = await core.server.request(
                `${core.config.backendAPI}/test/tasks/${tid}/annotation-counts`,
                { method: 'GET' },
            );
            setState({ status: 'loaded', data: response.data });
        } catch (error: unknown) {
            setState({ status: 'failed', message: error instanceof Error ? error.message : String(error) });
        }
    }, [tid]);

    useEffect(() => {
        load();
    }, [load]);

    let content: JSX.Element;
    if (state.status === 'loading') {
        content = <CVATLoadingSpinner />;
    } else if (state.status === 'failed') {
        content = (
            <Result
                status='error'
                title='Could not load annotation counts'
                subTitle={state.message}
                extra={<Button type='primary' onClick={load}>Retry</Button>}
            />
        );
    } else if (state.data.total === 0) {
        content = <Empty description='This task has no annotations yet' />;
    } else {
        const labelsWithAnnotations = state.data.labels.filter((label) => label.count > 0);
        const emptyLabels = state.data.labels.length - labelsWithAnnotations.length;
        content = (
            <>
                <div className='cvat-annotation-counts-summary'>
                    <Text type='secondary'>
                        {`${state.data.total} annotations across ${labelsWithAnnotations.length} labels`}
                        {emptyLabels > 0 ? ` (${emptyLabels} labels have none)` : ''}
                    </Text>
                    <Radio.Group
                        value={grouping}
                        onChange={(event) => setGrouping(event.target.value)}
                        optionType='button'
                        options={[
                            { label: 'Total', value: 'total' },
                            { label: 'By annotation type', value: 'type' },
                        ]}
                    />
                </div>
                <AnnotationCountsChart
                    labels={labelsWithAnnotations}
                    types={state.data.types}
                    grouping={grouping}
                />
            </>
        );
    }

    return (
        <div className='cvat-annotation-counts-page'>
            <Row justify='center'>
                <Col span={22} xl={18} xxl={14}>
                    <GoBackButton />
                    <Title level={4}>{`Annotation counts for task #${tid}`}</Title>
                    {content}
                </Col>
            </Row>
        </div>
    );
}

export default React.memo(AnnotationCountsPage);
